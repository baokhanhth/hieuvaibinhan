document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("q");
    const searchResult = document.getElementById("search-result");

    if (!searchInput || !searchResult) return;

    searchInput.addEventListener("input", async function () {
        const keyword = this.value.trim();
        
        if (!keyword) {
            searchResult.innerHTML = "";
            searchResult.style.display = "none";
            return;
        }

        try {
            const response = await fetch(`/inventory/purchases/search-purchase/?q=${encodeURIComponent(keyword)}`);
            const result = await response.json();
            
            if (!result.success || result.data.length === 0) {
                searchResult.innerHTML = `<div class="search-empty">Không tìm thấy phiếu nhập phù hợp.</div>`;
                searchResult.style.display = "block";
                return;
            }

            searchResult.innerHTML = result.data.map(purchase => `
                <div class="search-item" data-id="${purchase.id}">
                    <div class="item-title">${purchase.purchase_code} - ${purchase.supplier_name}</div>
                    <div class="item-meta">
                        <span class="status ${purchase.status}" style="font-size: 12px; padding: 2px 8px; border-radius: 10px;">${purchase.status_display}</span> 
                        • <span style="color:#dc3545; font-weight:bold;">${Number(purchase.total_amount).toLocaleString("vi-VN")} đ</span>
                    </div>
                </div>
            `).join("");
            
            searchResult.style.display = "block";
        } catch (error) {
            console.error("Lỗi tìm kiếm phiếu nhập", error);
            searchResult.style.display = "none";
        }
    });

    searchResult.addEventListener("click", function (event) {
        const item = event.target.closest(".search-item");
        if (!item) return;

        const purchaseId = item.dataset.id;
        window.location.href = `/inventory/purchases/${purchaseId}/`; 
    });

    document.addEventListener("click", function (event) {
        if (!searchResult.contains(event.target) && event.target !== searchInput) {
            searchResult.style.display = "none";
        }
    });
});
