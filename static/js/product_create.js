document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("createProductForm");
    const btnSave = document.getElementById("btnSave");

    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const name = document.getElementById("id_name").value.trim();
        const costPrice = parseFloat(document.getElementById("id_cost_price").value);
        const profitMargin = parseFloat(document.getElementById("id_profit_margin")?.value || 0);
        const stockQuantity = parseFloat(document.getElementById("id_stock_quantity").value);
        const minimumStock = parseFloat(document.getElementById("id_minimum_stock").value);
        const status = document.getElementById("id_status").value;

        if (!name) {
            Swal.fire({
                icon: "warning",
                title: "Cảnh báo",
                text: "Vui lòng nhập tên mặt hàng!",
                showCloseButton: true,
                confirmButtonText: "Đóng"
            });
            return;
        }

        // Kiểm tra thống nhất Giá vốn phải > 0
        if (isNaN(costPrice) || costPrice <= 0) {
            Swal.fire({
                icon: "warning",
                title: "Cảnh báo",
                text: "Giá vốn phải lớn hơn 0!",
                showCloseButton: true,
                confirmButtonText: "Đóng"
            });
            return;
        }

        if (isNaN(profitMargin) || profitMargin < 0) {
            Swal.fire({
                icon: "warning",
                title: "Cảnh báo",
                text: "% Lợi nhuận không được nhỏ hơn 0!",
                showCloseButton: true,
                confirmButtonText: "Đóng"
            });
            return;
        }

        if (isNaN(stockQuantity) || stockQuantity <= 0) {
            Swal.fire({
                icon: "warning",
                title: "Cảnh báo",
                text: "Tồn kho ban đầu phải lớn hơn 0!",
                showCloseButton: true,
                confirmButtonText: "Đóng"
            });
            return;
        }

        if (isNaN(minimumStock) || minimumStock <= 0) {
            Swal.fire({
                icon: "warning",
                title: "Cảnh báo",
                text: "Tồn kho tối thiểu phải lớn hơn 0!",
                showCloseButton: true,
                confirmButtonText: "Đóng"
            });
            return;
        }

        btnSave.disabled = true;
        btnSave.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang kiểm tra...`;

        try {
            const response = await fetch(window.location.pathname, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    name: name,
                    cost_price: costPrice,
                    profit_margin: profitMargin,
                    stock_quantity: stockQuantity,
                    minimum_stock: minimumStock,
                    status: status
                })
            });

            const data = await response.json();

            if (data.success) {
                Swal.fire({
                    icon: "success",
                    title: "Thành công!",
                    text: data.message,
                    timer: 1500,
                    showConfirmButton: false,
                    showCloseButton: true
                }).then(() => {
                    window.location.href = `/inventory/product-detail/${data.product_id}/`;
                });
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Không hợp lệ",
                    text: data.message,
                    showCloseButton: true,
                    confirmButtonText: "Đóng"
                });
                btnSave.disabled = false;
                btnSave.innerHTML = `<i class="fa-solid fa-floppy-disk"></i> Thêm`;
            }

        } catch (error) {
            console.error("Lỗi:", error);
            Swal.fire({
                icon: "error",
                title: "Lỗi",
                text: "Không thể kết nối đến máy chủ.",
                showCloseButton: true,
                confirmButtonText: "Đóng"
            });
            btnSave.disabled = false;
            btnSave.innerHTML = `<i class="fa-solid fa-floppy-disk"></i> Thêm`;
        }
    });
});