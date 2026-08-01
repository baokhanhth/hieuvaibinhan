function parseOrderCode(code) {return Number(String(code).replace(/\D/g, "")) || 0;}

function formatOrderCode(orderId) {return `HDB${String(orderId).padStart(7, "0")}`;}

let currentOrderId = parseOrderCode(document.getElementById("invoice-code").textContent);

const params = new URLSearchParams(window.location.search);
const orderId = params.get("order");

if (orderId) {currentOrderId = Number(orderId);}
let orderItems = [];
let isSaved = false;
let discount = 0;
let paid = 0;
let currentProducts = []
let totalAmount = 0;


const orderTable = document.getElementById("order-items");
const subtotalElement = document.getElementById("subtotal");
const totalElement = document.getElementById("total");
const discountInput = document.getElementById("discount");
const paidInput = document.getElementById("paid");
const changeElement = document.getElementById("change");
const btnNewInvoice = document.getElementById("btn-new-invoice");
const btnSave = document.getElementById("btn-save");
const btnCheckout = document.getElementById("btn-checkout");
const orderStatus = document.getElementById("order-status");
const invoiceCode = document.getElementById("invoice-code");
const noteInput = document.getElementById("note");
const csrfToken = document.getElementById("csrf-token").value;
const todayElement = document.getElementById("today");
const searchInput = document.getElementById("search-product");
const searchResult = document.getElementById("search-result");
const btnCloseInvoice = document.getElementById("btn-close-invoice");
const btnCancelOrder = document.getElementById("btn-cancel-order");

if (todayElement) {
    const now = new Date();
    const date = now.toLocaleDateString("vi-VN");
    todayElement.textContent = date;
}

function formatMoney(value){
    return Number(value).toLocaleString("vi-VN") + " đ";
}

function parseMoney(value){
    return Number(String(value).replace(/\D/g, "")) || 0;
}

function getHeaders(){
    return{
        "Content-Type":"application/json",
        "X-CSRFToken":csrfToken
    };
}

function attachMoneyInput(inputElement, onChangeCallback) {
    inputElement.addEventListener("keydown", function(e) {
        if (e.key === "-" || e.key === "e") {
            e.preventDefault();
        }
    });

    inputElement.addEventListener("input", function () {
        const money = parseMoney(this.value);
        if (typeof onChangeCallback === "function") {onChangeCallback(money);}});

    inputElement.addEventListener("blur", function () {
        const money = parseMoney(this.value);
        this.value = money ? formatMoney(money) : "";});

    inputElement.addEventListener("focus", function () {
        this.value = parseMoney(this.value) || "";

    });

}

searchInput.addEventListener("input", async function () {
    const keyword = this.value.trim();
    if (!keyword) {
        searchResult.innerHTML = "";
        searchResult.style.display = "none";
        return;
    }
    await searchProducts(keyword);
});

async function searchProducts(keyword) {

    try {   const response = await fetch(
            `/sales/products/search-sale/?q=${encodeURIComponent(keyword)}`
        );
        
        const result = await response.json();

        if (!result.success) {
            return;
        }
        currentProducts = result.data;
        renderSearchResult(currentProducts);
    }
    catch (error) {console.error(error);}
}

function renderSearchResult(products) {
    searchResult.innerHTML = "";
    if (products.length === 0) {
        searchResult.innerHTML = `
            <div class="search-empty">
                <div> Không tìm thấy loại vải này. Bạn có muốn thêm sản phẩm mới? </div>
                <div class="search-create"> 
                <a href="/inventory/create/">
                    Thêm mới
                </a>
                </div>
            </div>
        `;
        searchResult.style.display = "block";
        return;
    }

    products.forEach(product => {
        searchResult.innerHTML += `
            <div class="search-item" data-id="${product.id}">
                <div>${product.name}</div>
                <small>${formatMoney(product.selling_price)}</small>
            </div>
        `;
    });
    searchResult.style.display = "block";
}

// Thêm sản phẩm vừa tìm thấy vào hóa đơn
searchResult.addEventListener("click", async function (e) {
    const item = e.target.closest(".search-item");
    if (!item) {return;}

    const id = Number(item.dataset.id);
    const product = currentProducts.find(p => p.id === id);

    if (!product) {return;}

    await addProduct(product);
    searchInput.value = "";
    searchResult.innerHTML = "";
    searchResult.style.display = "none";
});

//ẩn danh sách tìm kiếm
document.addEventListener("click", function (e) {

    if (
        !searchInput.contains(e.target) &&
        !searchResult.contains(e.target)
    ) {
        searchResult.style.display = "none";
    }

});

async function addProduct(product) {
    if (!currentOrderId) {
        Swal.fire({ icon: "warning",
                    title: "Chưa có hóa đơn",
                    text: "Vui lòng tạo hóa đơn trước."});
        return;
    }

    try {
        const response = await fetch(
            `/sales/orders/${currentOrderId}/items/`,
            {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify({
                    product_id: product.id,
                    quantity: 1
                })
            }
        );

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.message);
        }

        await loadOrder(currentOrderId);
        isSaved = false;

    }
    catch (error)   {   Swal.fire({
                        icon: "error",
                        title: "Không thể thêm sản phẩm",
                        text: error.message,
                        showCloseButton: true,
                        confirmButtonText: "Đóng",
                    });
                    }

}

async function loadOrder(orderId) {
    const response = await fetch(`/sales/orders/${orderId}/data`);
    const result = await response.json();

    if (!result.success) {
        throw new Error(result.message);
    }

    const order = result.data;

    orderItems = order.items;
    discount = order.discount || 0;

    discountInput.value = discount
        ? formatMoney(discount)
        : "";
    orderStatus.textContent = order.status === "draft" ? "Chờ thanh toán": "Đã thanh toán";

    renderTable();
}

function updateCheckoutButton() {
    const hasItems = orderItems.length > 0;
    btnCheckout.disabled = !hasItems;

}

function updateCheckoutButton() {
    const hasItems = orderItems.length > 0;
    btnCheckout.disabled = !hasItems;
    discountInput.disabled = !hasItems;
    paidInput.disabled = !hasItems;
}

function renderTable() {
    orderTable.innerHTML = "";
    if (orderItems.length === 0) {
        orderTable.innerHTML = `
            <tr class="empty-row">
                <td colspan="5">
                    Chưa có sản phẩm trong hóa đơn
                </td>
            </tr>
        `;
        calculateInvoice();
        updateCheckoutButton();
        return;
    }

    orderItems.forEach(item => {
        const total = item.subtotal;
        orderTable.innerHTML += `
            <tr>
                <td>${item.product_name}</td>

                <td>
                    <input
                        type="number"
                        min="0.1"
                        step="0.1"
                        value="${item.quantity}"
                        oninput="if(this.value < 0) this.value = Math.abs(this.value)"
                        onchange="updateQuantity(${item.id}, this.value)">
                </td>
                <td>${formatMoney(item.unit_price)}</td>
                <td>${formatMoney(total)}</td>
                <td>
                    <button
                        class="remove-btn"
                        onclick="removeItem(${item.id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>

            </tr>
        `;

    });

    calculateInvoice();
    updateCheckoutButton();
}

async function updateQuantity(id, qty) {
    qty = parseFloat(qty);

    if (isNaN(qty) || qty <= 0) {
        Swal.fire({
            icon: "warning",
            title: "Số lượng không hợp lệ",
            text: "Số lượng sản phẩm phải lớn hơn 0.",
            timer: 1500,
            showConfirmButton: true,
            showCloseButton: true
        });
        await loadOrder(currentOrderId);
        return;
    }

    const response = await fetch(
        `/sales/orders/${currentOrderId}/items/${id}/`,
        {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify({
                quantity: qty
            })
        }
    );

    const result = await response.json();
    if (!result.success) {
        Swal.fire({
            icon: "error",
            text: result.message,
            showCloseButton: true,
            confirmButtonText: "Đóng",
        });
        return;
    }
    await loadOrder(currentOrderId);

}

async function removeItem(id){
    const response = await fetch(
        `/sales/orders/${currentOrderId}/items/${id}/`,
        {
            method:"DELETE",
            headers:getHeaders()
        }
    );

    const result = await response.json();
    if(!result.success){
        Swal.fire({
            icon:"error",
            text:result.message,
            showCloseButton: true,
            confirmButtonText: "Đóng",
        });
        return;
    }
    await loadOrder(currentOrderId);
}

function calculateInvoice(){
    let subtotal = 0;
    orderItems.forEach(item=>{subtotal += item.subtotal;    });

    let total = subtotal - discount;

    if(total < 0){
        total = 0;
    }
    subtotalElement.innerText = formatMoney(subtotal);
    totalAmount = total;
    totalElement.innerText = formatMoney(total);
    calculateChange();
}

function calculateChange(){
    let subtotal = 0;
    orderItems.forEach(item=>{ subtotal += item.subtotal;});
    let total = subtotal - discount;
    let change = paid - total;    
    if(change<0){
        change=0;
    }
    changeElement.innerText = formatMoney(change);
}

function invoiceHasData(){
    return orderItems.length > 0
        || discount > 0
        || paid > 0
        || noteInput.value.trim() !== "";
}

function clearInvoice(){
    orderItems = [];
    discount = 0;
    paid = 0;

    discountInput.value = "";
    paidInput.value = "";
    noteInput.value = "";
    isSaved = false;
    renderTable();
    updateCheckoutButton();
}

attachMoneyInput(discountInput, function(value){
    discount = value;
    calculateInvoice();
});

attachMoneyInput(paidInput, function(value){
    paid = value;
    calculateChange();
});

async function checkout() {
    if (orderItems.length === 0) {Swal.fire   ({
                                                    icon: "error",
                                                    title: "Chưa có sản phẩm",
                                                    text: "Vui lòng thêm ít nhất một sản phẩm.",
                                                    showCloseButton: true,
                                                    confirmButtonText: "Đóng",
                                                });
        return false;
    }

    if (paid <= 0) {    Swal.fire   ({
                                        icon: "warning",
                                        title: "Chưa nhập tiền thanh toán",
                                        text: "Vui lòng nhập số tiền khách thanh toán.",
                                        showCloseButton: true,
                                        confirmButtonText: "Đóng",
                                    });
        return false;
    }

    const total = parseMoney(totalElement.textContent);
    if (paid < totalAmount || paid < 0) { Swal.fire({
                                    icon: "warning",
                                    title: "Thanh toán không hợp lệ",
                                    text: "Số tiền khách thanh toán phải lớn hơn hoặc bằng số tiền cần thanh toán.",
                                    showCloseButton: true,
                                    confirmButtonText: "Đóng",
                                });
        return false;
    }

    try {

        const response = await fetch(`/sales/orders/${currentOrderId}/checkout/`,
            {   method: "POST",
                headers: getHeaders(),
            }
        );

        const result = await response.json();

        if (!result.success) { throw new Error(result.message);}

        currentOrderId = result.data.next_order_id;
        invoiceCode.textContent = formatOrderCode(currentOrderId);
        paid = 0;
        paidInput.value = "";
        noteInput.value = "";
        discount = 0;
        discountInput.value = "";

        await loadOrder(currentOrderId);

        const invoiceUrl = result.data.invoice_url;
        const swalResult = await Swal.fire({    icon: "success",
                                                title: "Thanh toán thành công",
                                                text: "Bạn có muốn in hóa đơn không?",
                                                showCloseButton: true,
                                                showCancelButton: true,
                                                confirmButtonText: "🖨️ In hóa đơn",
                                                cancelButtonText: "Đóng"});
        {if (swalResult.isConfirmed) {window.open(invoiceUrl, "_blank");}}
        return true;

    } catch (error) {   Swal.fire   ({  icon: "error",
                                        title: "Lỗi",
                                        text: error.message,
                                        showCloseButton: true,
                                        confirmButtonText: "Đóng",
                                    });

        return false;
    }
}

async function showInvoiceActionPopup() {

    if (!invoiceHasData()) {
        clearInvoice();
        return;
    }

    const result = await Swal.fire({
        title: "Hóa đơn chưa thanh toán",
        text: "Trước khi tạo hóa đơn mới, bạn muốn làm gì với hóa đơn hiện tại?",
        icon: "warning",
        showCloseButton: true,
        showCancelButton: true,
        showDenyButton: true,
        confirmButtonText: "💾 Thanh toán",
        denyButtonText: "🗑️ Xóa hóa đơn",
        cancelButtonText: "❌ Tiếp tục chỉnh sửa",
        confirmButtonColor: "#198754",
        denyButtonColor: "#dc3545",
        cancelButtonColor: "#6c757d"
    });

    if (result.isConfirmed) {
        await checkout();
    }
    else if (result.isDenied) {
        try {   const response = await fetch("/sales/orders/new-draft/",
                                                {   method: "POST",
                                                    headers: getHeaders(),});

                const result = await response.json();

                if (!result.success) {throw new Error(result.message);}

                currentOrderId = result.data.order_id;
                invoiceCode.textContent = formatOrderCode(currentOrderId);

                paid = 0;
                discount = 0;

                paidInput.value = "";
                discountInput.value = "";
                noteInput.value = "";

                await loadOrder(currentOrderId);

                Swal.fire({ icon: "success", title: "Đã tạo hóa đơn mới", timer: 1200, showConfirmButton: false,});} 
                
            catch (error) { Swal.fire({ icon: "error", title: "Lỗi", text: error.message, showCloseButton: true, confirmButtonText: "Đóng", }); 
        }
    }
}

if (btnSave) {btnSave.addEventListener("click", async () => {await saveInvoice();});}

btnNewInvoice.addEventListener("click", showInvoiceActionPopup);
btnCloseInvoice.addEventListener("click", showInvoiceActionPopup);
btnCancelOrder.addEventListener("click", showInvoiceActionPopup);
btnCheckout.addEventListener("click", checkout);

document.addEventListener("DOMContentLoaded", async () => { if (currentOrderId) {
        await loadOrder(currentOrderId);}
    updateCheckoutButton();
});

