document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("q");
    const searchResult = document.getElementById("search-result");
    const searchForm = document.getElementById("searchForm");

    if (!searchInput || !searchResult || !searchForm) {
        return;
    }

    searchInput.addEventListener("input", async function () {
        const keyword = this.value.trim();
        if (!keyword) {
            searchResult.innerHTML = "";
            searchResult.style.display = "none";
            return;
        }

        try {
            const response = await fetch(`/inventory/products/search/?q=${encodeURIComponent(keyword)}`);
            const result = await response.json();
            if (!result.success) {
                searchResult.innerHTML = "";
                searchResult.style.display = "none";
                return;
            }

            renderSearchResult(result.data);
        } catch (error) {
            console.error("Product search failed", error);
            searchResult.innerHTML = "";
            searchResult.style.display = "none";
        }
    });

    function renderSearchResult(products) {
        if (!products.length) {
            searchResult.innerHTML = `
                <div class="search-empty">
                    Không tìm thấy kết quả. Bạn có thể thêm mặt hàng mới.
                </div>
            `;
            searchResult.style.display = "block";
            return;
        }

        searchResult.innerHTML = products.map(product => `
            <div class="search-item" data-id="${product.id}">
                <div class="item-title">${product.fabric_code} - ${product.name}</div>
                <div class="item-meta">${product.stock_quantity} mét • ${formatMoney(product.selling_price)}</div>
            </div>
        `).join("");
        searchResult.style.display = "block";
    }

    function formatMoney(value) {
        return Number(value).toLocaleString("vi-VN") + " đ";
    }

    searchResult.addEventListener("click", function (event) {
        const item = event.target.closest(".search-item");
        if (!item) {
            return;
        }

        const productId = item.dataset.id;
        if (productId) {
            window.location.href = `/inventory/product-detail/${productId}/`;
        }
    });

    document.addEventListener("click", function (event) {
        if (!searchResult.contains(event.target) && event.target !== searchInput) {
            searchResult.style.display = "none";
        }
    });
});
