document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("q");
    const statusSelect = document.getElementById("status");
    const tableBody = document.getElementById("product-table-body");
    const productPage = document.getElementById("product-page");
    const searchForm = document.getElementById("searchForm");
    
    // Kiểm tra xem người dùng hiện tại có phải Owner hay không
    const isOwner = productPage ? productPage.dataset.isOwner === "true" : false;

    if (!searchInput || !tableBody) return;

    let debounceTimer = null;

    // Hàm gọi API và cập nhật trực tiếp vào <tbody>
    async function fetchAndRenderTable() {
        const keyword = searchInput.value.trim();
        const status = statusSelect ? statusSelect.value : "";

        try {
            const url = `/inventory/products/search/?q=${encodeURIComponent(keyword)}&status=${encodeURIComponent(status)}`;
            const response = await fetch(url);
            const result = await response.json();

            if (!result.success) {
                renderEmptyTable("Không tải được dữ liệu.");
                return;
            }

            renderTableBody(result.data);
        } catch (error) {
            console.error("Lỗi tìm kiếm sản phẩm:", error);
            renderEmptyTable("Không thể kết nối đến máy chủ.");
        }
    }

    // Hàm vẽ lại danh sách các dòng trong <tbody>
    function renderTableBody(products) {
        if (!products || products.length === 0) {
            renderEmptyTable("Không tìm thấy mặt hàng phù hợp.");
            return;
        }

        tableBody.innerHTML = products.map(product => {
            const isLowStock = product.stock_quantity <= product.minimum_stock;
            const rowClass = isLowStock ? "low-stock" : "";
            const cursorStyle = isOwner ? 'style="cursor:pointer;"' : '';
            const clickAttr = isOwner ? `onclick="window.location='${product.detail_url}'"` : '';

            const costPriceTd = isOwner 
                ? `<td>${formatMoney(product.cost_price)}</td>` 
                : '';

            const warningSpan = isLowStock 
                ? `<span class="warning"><i class="fa-solid fa-triangle-exclamation"></i> Cảnh báo</span>` 
                : '';

            return `
                <tr class="${rowClass}" ${cursorStyle} ${clickAttr}>
                    <!-- 1. ĐÃ SỬA: Dùng product.fabric_code thay vì product.id -->
                    <td>${escapeHtml(product.fabric_code)}</td>
                    <td>${escapeHtml(product.name)}</td>
                    ${costPriceTd}
                    <td>${formatMoney(product.selling_price)}</td>
                    <td>
                        ${Number(product.stock_quantity).toFixed(2)}
                        ${warningSpan}
                    </td>
                    <td>
                        <span class="status ${product.status}">${escapeHtml(product.status_display)}</span>
                    </td>
                </tr>
            `;
        }).join("");
    }

    function renderEmptyTable(message) {
        const colSpan = isOwner ? 6 : 5;
        tableBody.innerHTML = `
            <tr>
                <td colspan="${colSpan}" class="empty-state">
                    ${message}
                </td>
            </tr>
        `;
    }

    function formatMoney(value) {
        return Number(value || 0).toLocaleString("vi-VN") + " đ";
    }

    function escapeHtml(text) {
        if (!text) return "";
        return String(text)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Tự động tìm kiếm sau khi ngừng gõ 300ms (Debounce)
    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchAndRenderTable();
        }, 300);
    });

    // Thay đổi trạng thái lọc cũng cập nhật lại bảng lập tức
    if (statusSelect) {
        statusSelect.addEventListener("change", () => {
            fetchAndRenderTable();
        });
    }

    // Chặn reload trang khi bấm Enter ở ô tìm kiếm
    if (searchForm) {
        searchForm.addEventListener("submit", (e) => {
            e.preventDefault();
            fetchAndRenderTable();
        });
    }
});