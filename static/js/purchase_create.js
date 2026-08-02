document.addEventListener("DOMContentLoaded", () => {
    const csrfTokenEl = document.getElementById("csrf-token");
    const csrfToken = csrfTokenEl ? csrfTokenEl.value : "";

    const searchInput = document.getElementById("search-product");
    const searchResult = document.getElementById("search-result");
    const tBody = document.querySelector(".items-table tbody") || document.getElementById("purchase-items-body") || document.getElementById("purchase-items");
    const supplierName = document.getElementById("supplier-name");
    const supplierPhone = document.getElementById("supplier-phone");
    const totalAmount = document.getElementById("total-amount");
    const btnSave = document.getElementById("btn-save");
    const btnCancel = document.getElementById("btn-cancel");

    let purchaseItems = [];
    let currentProducts = [];

    function formatMoney(value) {
        return Number(value || 0).toLocaleString("vi-VN") + " đ";
    }

    const todayElement = document.getElementById("current-date");
    if (todayElement) {
        todayElement.textContent = new Date().toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric" });
    }

    function calculateTotal() {
        let total = 0;
        purchaseItems.forEach(item => {
            total += item.quantity * item.unit_price;
        });
        if (totalAmount) totalAmount.textContent = formatMoney(total);
    }

    function hideSearchResult() {
        if (searchResult) {
            searchResult.innerHTML = "";
            searchResult.style.display = "none";
        }
    }

    // Ẩn menu khi click ra ngoài
    document.addEventListener("click", function (e) {
        if (searchInput && searchResult && !searchInput.contains(e.target) && !searchResult.contains(e.target)) {
            hideSearchResult();
        }
    });

    // Bắt sự kiện gõ ô tìm kiếm
    if (searchInput) {
        searchInput.addEventListener("input", async function () {
            const keyword = this.value.trim();
            if (!keyword) {
                currentProducts = [];
                hideSearchResult();
                return;
            }
            await searchProducts(keyword);
        });
    }

    async function searchProducts(keyword) {
        try {
            const response = await fetch(`/inventory/purchase/search-product/?q=${encodeURIComponent(keyword)}`);
            const result = await response.json();

            if (!result.success) {
                currentProducts = [];
                renderSearchResult(keyword);
                return;
            }
            currentProducts = result.data || [];
            renderSearchResult(keyword);
        } catch (error) {
            console.error("Lỗi tìm kiếm sản phẩm:", error);
        }
    }

    function renderSearchResult(keyword) {
        if (!searchResult) return;
        searchResult.innerHTML = "";

        if (currentProducts.length === 0) {
            searchResult.innerHTML = `
                <div class="search-empty" style="padding: 12px; text-align: center;">
                    <div style="margin-bottom: 8px; color: #555;"> Không tìm thấy loại vải này. Bạn có muốn thêm sản phẩm mới? </div>
                    <div class="search-create"> 
                        <a href="/inventory/create/" target="_blank" class="btn-add-new" style="display: inline-block; padding: 6px 16px; background-color: #0d6efd; color: white; border-radius: 6px; text-decoration: none; font-weight: 600;">
                            + Thêm mới
                        </a>
                    </div>
                </div>
            `;
            searchResult.style.display = "block";
            return;
        }

        let html = currentProducts.map(product => `
            <div class="search-item" data-id="${product.id}" style="padding: 10px; border-bottom: 1px solid #f0f0f0; cursor: pointer;">
                <div><strong>${product.name} </strong>  </div>
            </div>
        `).join("");

        searchResult.innerHTML = html;
        searchResult.style.display = "block";
    }

    // Bắt sự kiện chọn item từ dropdown
    if (searchResult) {
        searchResult.addEventListener("click", function (e) {
            const item = e.target.closest(".search-item");
            if (!item) return;

            const id = Number(item.dataset.id);
            const product = currentProducts.find(p => p.id === id);

            if (product) {
                addProduct(product);
                if (searchInput) searchInput.value = "";
                hideSearchResult();
            }
        });
    }

    function addProduct(product) {
        const exist = purchaseItems.find(item => item.product_id === product.id);

        if (exist) {
            exist.quantity += 1;
        } else {
            purchaseItems.push({
                product_id: product.id,
                fabric_code: product.fabric_code,
                name: product.name,
                quantity: 1,
                unit_price: Number(product.cost_price) || 0,
            });
        }
        renderTable();
    }

    function renderTable() {
        if (!tBody) return;
        tBody.innerHTML = "";

        if (!purchaseItems.length) {
            tBody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="7" style="text-align: center; color: #888; padding: 25px;">
                        Chưa có mặt hàng nào.
                    </td>
                </tr>
            `;
            calculateTotal();
            if (btnSave) btnSave.disabled = true;
            return;
        }

        if (btnSave) btnSave.disabled = false;

        purchaseItems.forEach((item, index) => {
            const subtotal = item.quantity * item.unit_price;

            tBody.innerHTML += `
                <tr>
                    <td style="text-align:center;">${index + 1}</td>
                    <td>${item.fabric_code}</td>
                    <td>${item.name}</td>
                    <td style="text-align:center;">
                        <input
                            type="number"
                            class="quantity-input"
                            min="0.1"
                            step="0.1"
                            value="${item.quantity}"
                            onchange="updateQuantity(${index}, this.value)">
                    </td>
                    <td>
                        <input
                            type="number"
                            class="price-input"
                            value="${item.unit_price}"
                            min="0"
                            step="1000"
                            onchange="updatePrice(${index}, this.value)">
                    </td>
                    <td style="text-align:right;">${formatMoney(subtotal)}</td>
                    <td style="text-align:center;">
                        <button
                            type="button"
                            class="remove-btn"
                            onclick="removeItem(${index})">
                            <i class="fa-solid fa-trash" style="color: #dc3545;"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        calculateTotal();
    }

    window.updateQuantity = function(index, value) {
        let quantity = parseFloat(value);
        if (isNaN(quantity) || quantity <= 0) quantity = 1;
        purchaseItems[index].quantity = quantity;
        renderTable();
    };

    window.updatePrice = function(index, value) {
        let price = parseFloat(value);
        if (isNaN(price) || price < 0) price = 0;
        purchaseItems[index].unit_price = price;
        renderTable();
    };

    window.removeItem = function(index) {
        purchaseItems.splice(index, 1);
        renderTable();
    };

    // Lưu phiếu nhập
    if (btnSave) {
        btnSave.addEventListener("click", async function () {
            if (purchaseItems.length === 0) {
                if (typeof Swal !== "undefined") 
                    Swal.fire({ icon: "warning",
                                title: "Cảnh báo", 
                                text: "Vui lòng chọn ít nhất 1 mặt hàng!", 
                                showClostutton: true,
                                showConfirmButton: true,
                                confirmButtonText: "Đóng"
            });
                return;
            }

            btnSave.disabled = true;
            btnSave.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang lưu...`;

            try {
                const response = await fetch("/inventory/purchase/create/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        supplier_name: supplierName ? supplierName.value.trim() : "",
                        supplier_phone: supplierPhone ? supplierPhone.value.trim() : "",
                        items: purchaseItems
                    })
                });

                const data = await response.json();
                if (data.success) {
                    if (typeof Swal !== "undefined") {
                        Swal.fire({ icon: "success",
                                    title: "Thành công!",
                                    text: "Đã lưu phiếu nhập thành công.",
                                    timer: 1500,
                                    showCloseButton: true,
                                    showConfirmButton: true,
                                confirmButtonText: "Đóng"} 
                                    ).then(() => {
                            window.location.href = data.data.redirect_url;
                        });
                    } else {
                        window.location.href = data.data.redirect_url;
                    }
                } else {
                    throw new Error(data.message || "Lỗi lưu phiếu nhập.");
                }
            } catch (err) {
                if (typeof Swal !== "undefined") Swal.fire("Lỗi", err.message, "error");
                btnSave.disabled = false;
                btnSave.innerHTML = "Lưu phiếu nhập";
            }
        });
    }

    renderTable();
});