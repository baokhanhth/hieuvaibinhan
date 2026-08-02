document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("q");
    const tableBody = document.getElementById("purchase-list-body");
    const searchForm = document.getElementById("searchForm");

    if (!searchInput || !tableBody) return;

    let debounceTimer = null;

    async function fetchAndRenderPurchases() {
        const keyword = searchInput.value.trim();

        try {
            const response = await fetch(`/inventory/purchase/search/?q=${encodeURIComponent(keyword)}`);
            const result = await response.json();

            if (!result.success || !result.data || result.data.length === 0) {
                renderEmptyTable("Không tìm thấy phiếu nhập nào phù hợp.");
                return;
            }

            renderTableBody(result.data);
        } catch (error) {
            console.error("Lỗi tìm kiếm phiếu nhập:", error);
            renderEmptyTable("Không thể kết nối tới máy chủ.");
        }
    }

    function renderTableBody(purchases) {
        tableBody.innerHTML = purchases.map(p => `
            <tr class="purchase-row" onclick="window.location='/inventory/purchase/${p.id}/'" style="cursor: pointer;">
                <td><strong>${escapeHtml(p.purchase_code)}</strong></td>
                <td>${escapeHtml(p.supplier_name)}</td>
                <td>${escapeHtml(p.created_at)}</td>
                <td class="total-money">${formatMoney(p.total_amount)}</td>
                <td><i class="fa-solid fa-eye"></i></td>
            </tr>
        `).join("");
    }

    function renderEmptyTable(message) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state" style="text-align: center; padding: 30px; color: #666;">
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

    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchAndRenderPurchases();
        }, 300);
    });

    if (searchForm) {
        searchForm.addEventListener("submit", (e) => {
            e.preventDefault();
            fetchAndRenderPurchases();
        });
    }
});