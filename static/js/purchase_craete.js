const csrfToken = document.getElementById("csrf-token").value;

const searchInput = document.getElementById("search-product");
const searchResult = document.getElementById("search-result");
const tbody = document.querySelector(".items-table tbody") || document.getElementById("purchase-items-body") || document.getElementById("purchase-items");
const totalAmount = document.getElementById("total-amount");

const supplierNameInput = document.getElementById("supplier-name");
const supplierPhoneInput = document.getElementById("supplier-phone");
const btnSave = document.getElementById("btn-save");
const btnCancel = document.getElementById("btn-cancel");

let purchaseItems = [];
let currentProducts = [];

function formatMoney(value) {
    return Number(value).toLocaleString("vi-VN") + " đ";
}

function parseMoney(value) {
    return Number(String(value).replace(/\D/g, "")) || 0;
}

function getHeaders() {
    return {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
    };
}

// Hiển thị ngày tháng hiện tại
const todayElement = document.getElementById("current-date");
if (todayElement) {
    todayElement.textContent = new Date().toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric" });
}

searchInput.addEventListener("input", async function () {
    const keyword = this.value.trim();
    if (!keyword) {
        searchResult.style.display = "none";
        searchResult.innerHTML = "";
        return;
    }

    try {
        const response = await fetch(`/inventory/products/search/?q=${encodeURIComponent(keyword)}`);
        const result = await response.json();

        if (result.success) {
            currentProducts = result.data;
            renderSearchResult(currentProducts, keyword);
        }
    } catch (error) {
        console.error("Lỗi tìm kiếm:", error);
    }
});

function renderSearchResult(products, keyword) {
    searchResult.innerHTML = "";

    if (products.length === 0) {
        searchResult.innerHTML = `
            <div class="search-item" data-new="true" style="color: #0d6efd; font-weight: 600; text-align: center;">
                <i class="fa-solid fa-plus"></i> Thêm mặt hàng mới: "${keyword}"
            </div>
        `;
        searchResult.style.display = "block";
        return;
    }

    let html = products.map(product => `
        <div class="search-item" data-id="${product.id}">
            <div><strong>${product.fabric_code}</strong> - ${product.name}</div>
            <div style="font-size: 13px; color: #666; margin-top: 4px;">
                <span>Tồn kho: <strong>${product.stock_quantity}</strong></span> | 
                <span>Giá vốn: <strong style="color:#28a745;">${formatMoney(float(product.cost_price))}</strong></span>
            </div>
        </div>
    `).join("");

    html += `
        <div class="search-item" data-new="true" style="color: #0d6efd; font-weight: 600; text-align: center; border-top: 1px dashed #ccc;">
            <i class="fa-solid fa-plus"></i> Hoặc thêm mới: "${keyword}"
        </div>
    `;

    searchResult.innerHTML = html;
    searchResult.style.display = "block";
}

// Xử lý sự kiện click vào kết quả tìm kiếm
searchResult.addEventListener("click", function (e) {
    const item = e.target.closest(".search-item");
    if (!item) return;

    if (item.dataset.new === "true") {
        // NẾU BẤM THÊM MỚI
        addNewProduct(searchInput.value.trim());
    } else {
        // NẾU CHỌN SẢN PHẨM CÓ SẴN
        const id = Number(item.dataset.id);
        const product = currentProducts.find(p => p.id === id);
        if (product) addProduct(product);
    }

    searchInput.value = "";
    searchResult.style.display = "none";
});

// Ẩn menu khi click ra ngoài
document.addEventListener("click", function (e) {
    if (!searchInput.contains(e.target) && !searchResult.contains(e.target)) {
        searchResult.style.display = "none";
    }
});

function addProduct(product) {
    const exist = purchaseItems.find(item => item.product_id === product.id);
    if (exist) {
        exist.quantity++;
    } else {
        purchaseItems.push({
            product_id: product.id,
            fabric_code: product.fabric_code,
            name: product.name,
            quantity: 1,
            unit_price: float(product.cost_price) || 0
        });
    }
    renderTable();
}

function addNewProduct(name) {
    const exist = purchaseItems.find(item => item.product_id === null && item.name.toLowerCase() === name.toLowerCase());
    if (exist) {
        exist.quantity++;
    } else {
        purchaseItems.push({
            product_id: null,
            fabric_code: "MỚI",
            name: name,
            quantity: 1,
            unit_price: 0
        });
    }
    renderTable();
}

window.updateQuantity = function(index, value) {
    let numValue = parseFloat(value);
    if (isNaN(numValue) || numValue <= 0) numValue = 1; 
    purchaseItems[index].quantity = numValue;
    renderTable();
}

window.updatePrice = function(index, value) {
    let numValue = parseMoney(value);
    if (isNaN(numValue) || numValue < 0) numValue = 0; 
    purchaseItems[index].unit_price = numValue;
    renderTable();
}

window.removeItem = function(index) {
    purchaseItems.splice(index, 1);
    renderTable();
}

function renderTable() {
    if (!purchaseItems.length) {
        tbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="7" style="text-align: center; color: #888; padding: 30px;">
                    Chưa có mặt hàng nào. Vui lòng tìm kiếm để nhập hàng!
                </td>
            </tr>
        `;
        calculateTotal();
        if (btnSave) btnSave.disabled = true;
        return;
    }

    let html = "";
    purchaseItems.forEach((item, index) => {
        const subtotal = item.quantity * item.unit_price;
        html += `
        <tr>

            <td style="text-align:center;">
                ${index + 1}
            </td>

            <td>
                ${item.fabric_code}
            </td>

            <td>
                ${item.name}
            </td>

            <td style="text-align:center;">

                <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value="${item.quantity}"
                    onchange="updateQuantity(${index}, this.value)">

            </td>

            <td>

                <input
                    type="text"
                    value="${formatMoney(item.unit_price)}"
                    onfocus="this.value=parseMoney(this.value)"
                    onblur="updatePrice(${index}, this.value)">

            </td>

            <td style="text-align:right;">

                ${formatMoney(subtotal)}

            </td>

            <td style="text-align:center;">

                <button
                    class="btn-delete"
                    onclick="removeItem(${index})">

                    <i class="fa-solid fa-trash"></i>

                </button>

            </td>

        </tr>
        `;
    });

    tbody.innerHTML = html;
    if (btnSave) btnSave.disabled = false;
    calculateTotal();
}

function calculateTotal() {
    let total = 0;
    purchaseItems.forEach(item => {
        total += item.quantity * item.unit_price;
    });
    if (totalAmount) totalAmount.innerText = formatMoney(total);
}

async function savePurchase() {
    if (purchaseItems.length === 0) {
        Swal.fire("Cảnh báo", "Phiếu nhập chưa có mặt hàng nào!", "warning");
        return;
    }

    const supplierName = supplierNameInput ? supplierNameInput.value.trim() : "";
    const supplierPhone = supplierPhoneInput ? supplierPhoneInput.value.trim() : "";

    btnSave.disabled = true;
    const originalText = btnSave.innerHTML;
    btnSave.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang lưu...`;

    try {
        const response = await fetch(`/inventory/purchase/create/`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({
                supplier_name: supplierName,
                supplier_phone: supplierPhone,
                items: purchaseItems
            })
        });

        const data = await response.json();

        if (data.success) {
            Swal.fire({
                icon: "success",
                title: "Thành công!",
                text: data.message || "Đã lưu phiếu nhập.",
                timer: 1500,
                showConfirmButton: false,
                showCloseButton: true
            }).then(() => {
                window.location.href = data.data.redirect_url;
            });
        } else {
            throw new Error(data.message || "Không thể lưu phiếu nhập.");
        }
    } catch (error) {
        Swal.fire("Lỗi", error.message, "error");
        btnSave.disabled = false;
        btnSave.innerHTML = originalText;
    }
}

function cancelPurchase() {
    if (purchaseItems.length === 0) {
        window.location.href = "/inventory/purchase/";
        return;
    }

    Swal.fire({
        title: "Hủy phiếu nhập?",
        text: "Dữ liệu bạn vừa nhập sẽ không được lưu lại.",
        icon: "warning",
        showCancelButton: true,
        showCloseButton: true,
        confirmButtonColor: "#dc3545",
        confirmButtonText: "Đồng ý hủy",
        cancelButtonText: "Tiếp tục sửa"
    }).then(result => {
        if (result.isConfirmed) {
            window.location.href = "/inventory/purchase/";
        }
    });
}

if (btnSave) btnSave.addEventListener("click", savePurchase);
if (btnCancel) btnCancel.addEventListener("click", cancelPurchase);

// Khởi tạo bảng rỗng lúc mới load
document.addEventListener("DOMContentLoaded", () => {
    renderTable();
});