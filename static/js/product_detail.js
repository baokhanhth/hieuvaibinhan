document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("editProductForm");
    // defensive: locate elements and bail early if page structure differs
    const btnEdit = document.getElementById("btnEdit");
    const btnCancel = document.getElementById("btnCancel");
    const btnSave = document.getElementById("btnSave");

    const nameInput = document.getElementById("id_name");
    const costPriceInput = document.getElementById("id_cost_price");
    const profitMarginInput = document.getElementById("id_profit_margin"); // Thêm trường % lợi nhuận
    const stockInput = document.getElementById("id_stock_quantity");
    const statusInput = document.getElementById("id_status");

    const sellingPriceInput = document.getElementById("selling-price");
    const minimumStockInput = document.getElementById("id_minimum_stock");
    
    // Nếu thiếu các element quan trọng thì dừng lại và báo lỗi
    const missing = [];
    if (!form) missing.push('form#editProductForm');
    if (!nameInput) missing.push('#id_name');
    if (!costPriceInput) missing.push('#id_cost_price');
    if (!profitMarginInput) missing.push('#id_profit_margin'); // Báo lỗi nếu thiếu input % LN
    if (!stockInput) missing.push('#id_stock_quantity');
    if (!minimumStockInput)    missing.push('#id_minimum_stock');
    if (!statusInput) missing.push('#id_status');
    if (!sellingPriceInput) missing.push('#selling-price');
    
    if (missing.length) {
        console.warn('product_detail.js: missing expected elements —', missing.join(', '));
        if (window.Swal) {
            Swal.fire({
                icon: 'error',
                title: 'Lỗi giao diện',
                text: 'Trang chi tiết hàng hóa thiếu phần tử cần thiết. Vui lòng tải lại trang hoặc báo kỹ thuật.',
                showCloseButton: true,
                closeButtonHtml: '&times;',
                confirmButtonText: 'Đóng'
            });
        }
        return;
    }

    const originalData = {};

    function saveOriginalData() {
        originalData.name = nameInput.value;
        originalData.costPrice = costPriceInput.value;
        originalData.profitMargin = profitMarginInput.value; // Lưu dữ liệu gốc % LN
        originalData.stock = stockInput.value;
        originalData.minimumStock = minimumStockInput.value;
        originalData.status = statusInput.value;
        originalData.sellingPrice = sellingPriceInput.value;
    }

    function restoreOriginalData() {
        nameInput.value = originalData.name;
        costPriceInput.value = originalData.costPrice;
        profitMarginInput.value = originalData.profitMargin; // Phục hồi dữ liệu gốc % LN
        stockInput.value = originalData.stock;
        minimumStockInput.value = originalData.minimumStock;
        statusInput.value = originalData.status;
        sellingPriceInput.value = originalData.sellingPrice;
    }

    function enableEdit(enable) 
    {   
        nameInput.readOnly = !enable;
        costPriceInput.readOnly = !enable;
        profitMarginInput.readOnly = true;
        profitMarginInput.disabled = true;
        stockInput.disabled = !enable;
        minimumStockInput.readOnly = true;
        minimumStockInput.disabled = true;
        minimumStockInput.value = 5;
        statusInput.disabled = !enable;

        if (enable) {
            btnEdit.classList.add("hidden");
            btnCancel.classList.remove("hidden");
            btnSave.classList.remove("hidden");
        } else {
            btnEdit.classList.remove("hidden");
            btnCancel.classList.add("hidden");
            btnSave.classList.add("hidden");
        }
    }

    // Thiết lập trạng thái ban đầu
    saveOriginalData();
    enableEdit(false);

    // Bắt sự kiện Chỉnh sửa / Hủy
    btnEdit.addEventListener("click", () => { enableEdit(true); });
    btnCancel.addEventListener("click", () => { restoreOriginalData(); enableEdit(false); });

    // Tự động tính giá bán: Giá bán = Giá vốn + (Giá vốn * % Lợi nhuận / 100)
    function calculateSellingPrice() {
        const cost = parseFloat(costPriceInput.value) || 0;
        const margin = parseFloat(profitMarginInput.value) || 0;

        if (isNaN(cost)) {
            sellingPriceInput.value = "";
            return;
        }
        const sellingPrice = cost + (cost * margin / 100);
        sellingPriceInput.value = Math.round(sellingPrice); // Làm tròn số
    }

    // Lắng nghe sự kiện gõ phím từ CẢ HAI ô Giá vốn và % Lợi nhuận
    costPriceInput.addEventListener("input", calculateSellingPrice);
    profitMarginInput.addEventListener("input", calculateSellingPrice);

    // Cập nhật lên máy chủ (Lưu chỉnh sửa)
    function getCompleteFormData() {
        const formData = new FormData(form);
        if (!formData.has('name') && nameInput) formData.set('name', nameInput.value);
        if (!formData.has('cost_price') && costPriceInput) formData.set('cost_price', costPriceInput.value);
        if (!formData.has('profit_margin') && profitMarginInput) formData.set('profit_margin', profitMarginInput.value || '30');
        if (!formData.has('stock_quantity') && stockInput) formData.set('stock_quantity', stockInput.value);
        if (!formData.has('minimum_stock') && minimumStockInput) formData.set('minimum_stock', '5');
        if (!formData.has('status') && statusInput) formData.set('status', statusInput.value || 'active');
        return formData;
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
            
        const formData = getCompleteFormData();
        try {
            const url = form.action || window.location.href;
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            
            const response = await fetch(url, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Accept": "application/json",
                },
                body: formData,
            });

            if (!response.ok) {
                const text = await response.text();
                let message = `Lỗi server ${response.status}`;
                try {
                    const json = JSON.parse(text);
                    if (json.message) message = json.message;
                } catch (parseError) {
                    if (text) message = text;
                }
                console.error("Product save failed", response.status, response.statusText, text);
                throw new Error(message);
            }

            const result = await response.json();

            if (!result.success) {
                Swal.fire({
                    icon: "error",
                    title: "Lỗi",
                    text: result.message,
                    showCloseButton: true,
                    closeButtonHtml: "&times;",
                    confirmButtonText: "Đóng",
                });
                return;
            }

            Swal.fire({
                icon: "success",
                title: "Thành công",
                text: result.message,
                showCloseButton: true,
                closeButtonHtml: "&times;",
                confirmButtonText: "Đóng",
            }).then(() => {
                window.location.reload();
            });
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Lỗi",
                text: error.message || "Không thể kết nối đến máy chủ.",
                showCloseButton: true,
                confirmButtonText: "Đóng",
            });
        }
    });

    // Xóa (đánh dấu Ngừng kinh doanh)
    const btnDelete = document.querySelector('.btn-delete');
    if (btnDelete) {
        btnDelete.addEventListener('click', async () => {
            const result = await Swal.fire({
                title: 'Bạn có chắc muốn xóa?',
                text: "Mặt hàng sẽ được đặt về trạng thái 'Ngừng kinh doanh' và không bị xóa hoàn toàn.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Xác nhận',
                cancelButtonText: 'Hủy',
                showCloseButton: true,
                closeButtonHtml: '&times;'
            });

            if (!result.isConfirmed) return;

            const url = form.action || window.location.href;
            const formData = getCompleteFormData();
            formData.set('status', 'inactive');

            try {
                const csrfEl = document.querySelector('input[name="csrfmiddlewaretoken"]');
                const csrfToken = csrfEl ? csrfEl.value : '';

                const resp = await fetch(url, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Accept': 'application/json'
                    },
                    body: formData,
                });

                if (!resp.ok) {
                    const text = await resp.text();
                    throw new Error(text || `Lỗi server ${resp.status}`);
                }

                const json = await resp.json();
                if (!json.success) {
                    throw new Error(json.message || 'Không thể cập nhật trạng thái.');
                }

                if (statusInput) statusInput.value = 'inactive';

                Swal.fire({
                    icon: 'success',
                    title: 'Đã cập nhật',
                    text: 'Mặt hàng đã được chuyển sang trạng thái Ngừng kinh doanh.',
                    showCloseButton: true,
                    closeButtonHtml: '&times;',
                    confirmButtonText: 'Đóng'
                }).then(() => {
                    window.location.reload();
                });

            } catch (err) {
                console.error('Mark inactive failed', err);
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: err.message || 'Không thể kết nối đến máy chủ.',
                    showCloseButton: true,
                    confirmButtonText: 'Đóng'
                });
            }
        });
    }
});