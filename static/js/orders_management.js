const csrfToken = document.getElementById("csrf-token")?.value;

function getHeaders() {
    return {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
    };
}

function formatOrderCode(id) {
    return "HDB" + String(id).padStart(7, "0");
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".order-row").forEach(row => {
        row.addEventListener("click", () => {
            const orderId = row.dataset.id;
            const orderStatus = row.dataset.status;
            
            if (orderStatus === "draft") { 
                window.location.href = `/sales/?order=${orderId}`;
            } else {
                window.location.href = `/sales/orders/${orderId}/`;
            }
        });
    });
});

let currentOrderId = null;

function openDeleteModal(id) {
    currentOrderId = id;
    document.getElementById("delete-order-code").textContent = formatOrderCode(id);
    document.getElementById("delete-order-modal").classList.add("active");
}

function closeDeleteModal() {
    document.getElementById("delete-order-modal").classList.remove("active");
}

function confirmDeleteOrder() {
    if (!currentOrderId) return;

    fetch(`/sales/orders/${currentOrderId}/delete/`, { 
        method: "DELETE",
        headers: getHeaders()
    })
    .then(response => response.json())
    .then(result => {
        if (!result.success) {
            Swal.fire({
                icon: "error",
                title: "Lỗi",
                text: result.message
            });
            return;
        }

        Swal.fire({
            icon: "success",
            title: "Thành công",
            text: "Đã xóa hóa đơn.",
            timer: 1500,
            showConfirmButton: false,
            showCloseButton: true,
        }).then(() => {
            window.location.reload(); 
        });
    })
    .catch(() => {
        Swal.fire({
            icon: "error",
            title: "Lỗi",
            text: "Không thể xóa hóa đơn.",
            showCloseButton: true,
        });
    });
}

// Đóng modal khi bấm ra ngoài
window.onclick = function(event) {
    const deleteModal = document.getElementById("delete-order-modal");
    if (event.target === deleteModal) {
        closeDeleteModal();
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("q");
    const searchResult = document.getElementById("search-result");

    if (!searchInput || !searchResult) return;

    // Lắng nghe sự kiện gõ chữ
    searchInput.addEventListener("input", async function () {
        const keyword = this.value.trim();
        
        if (!keyword) {
            searchResult.innerHTML = "";
            searchResult.style.display = "none";
            return;
        }

        try {
            // GỌI API CHUẨN XÁC
            const response = await fetch(`/sales/orders/search-order/?q=${encodeURIComponent(keyword)}`);
            const result = await response.json();
            
            if (!result.success || result.data.length === 0) {
                searchResult.innerHTML = `<div class="search-empty">Không tìm thấy hóa đơn phù hợp.</div>`;
                searchResult.style.display = "block";
                return;
            }

            searchResult.innerHTML = result.data.map(order => `
                <div class="search-item" data-id="${order.id}" data-status="${order.status}">
                    <div class="search-item-left">
                        <strong style="color: #073B68; font-size: 15px;">${order.order_code}</strong>
                        <div style="font-size: 13px; color: #555; margin-top: 4px;">
                            <i class="fa-solid fa-user"></i> ${order.employee_name}
                        </div>
                    </div>
                    <div class="search-item-right" style="text-align: right;">
                        <span class="status ${order.status}" style="font-size: 12px;">${order.status_display}</span>
                        <div style="color: #dc3545; font-weight: bold; margin-top: 5px;">
                            ${order.final_amount.toLocaleString('vi-VN')}đ
                        </div>
                    </div>
                </div>
            `).join("");
            
            searchResult.style.display = "block";
        } catch (error) {
            console.error("Lỗi tìm kiếm hóa đơn", error);
            searchResult.style.display = "none";
        }
    });

    document.addEventListener("click", function (event) {
        if (!searchResult.contains(event.target) && event.target !== searchInput) {
            searchResult.style.display = "none";
        }
    });

    searchResult.addEventListener("click", function (event) {
        const item = event.target.closest(".search-item");
        if (!item) return;

        const orderId = item.dataset.id;
        const orderStatus = item.dataset.status;

        if (orderStatus === "draft") {
            window.location.href = `/sales/?order=${orderId}`;
        } else {
            window.location.href = `/sales/orders/${orderId}/`;
        }
    });
});

function renderSearchResult(orders) {
        if (!orders.length) {
            searchResult.innerHTML = `
                <div class="search-empty">
                    Không tìm thấy hóa đơn phù hợp.
                </div>
            `;
            searchResult.style.display = "block";
            return;
        }

        searchResult.innerHTML = orders.map(order => `
            <div class="search-item" data-id="${order.id}" data-status="${order.status}">
                <div class="item-title">${order.order_code} - ${order.employee_name}</div>
                <div class="item-meta">
                    <span class="status ${order.status}" style="font-size: 12px; padding: 2px 8px; border-radius: 10px;">${order.status_display}</span> • ${Number(order.final_amount).toLocaleString("vi-VN")} đ
                </div>
            </div>
        `).join("");
        
        searchResult.style.display = "block";
    }