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
    const tableBody = document.getElementById("order-list-body");
    const searchForm = document.getElementById("searchForm");

    if (!searchInput || !tableBody) return;

    let debounceTimer = null;

    // Hàm gọi API tìm kiếm đơn hàng
    async function fetchAndRenderOrders() {
        const keyword = searchInput.value.trim();

        try {
            const url = `/sales/orders/search-order/?q=${encodeURIComponent(keyword)}`;
            const response = await fetch(url);
            const result = await response.json();

            if (!result.success) {
                renderEmptyTable("Không tải được dữ liệu.");
                return;
            }

            renderTableBody(result.data);
        } catch (error) {
            console.error("Lỗi tìm kiếm đơn hàng:", error);
            renderEmptyTable("Không thể kết nối đến máy chủ.");
        }
    }

    // Hàm render danh sách dòng <tr> vào <tbody>
    function renderTableBody(orders) {
        if (!orders || orders.length === 0) {
            renderEmptyTable("Không tìm thấy hóa đơn nào phù hợp.");
            return;
        }

        tableBody.innerHTML = orders.map(order => {
            return `
                <tr class="order-row"
                    data-id="${order.id}"
                    onclick="window.location='${order.detail_url}'"
                    style="cursor: pointer;">
                    
                    <td><strong>${escapeHtml(order.order_code)}</strong></td>
                    <td>${escapeHtml(order.employee_name)}</td>
                    <td>${escapeHtml(order.created_at)}</td>
                    <td class="total-money" style="color: #dc3545; font-weight: bold;">
                        ${formatMoney(order.final_amount)}
                    </td>
                    <td>
                        <span class="status ${order.status}">
                            ${escapeHtml(order.status_display)}
                        </span>
                    </td>
                    <td><i class="fa-solid fa-eye"></i></td>
                </tr>
            `;
        }).join("");
    }

    function renderEmptyTable(message) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state" style="text-align: center; padding: 30px; color: #666;">
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

    // Lắng nghe sự kiện gõ phím ở ô tìm kiếm (Debounce 300ms)
    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchAndRenderOrders();
        }, 300);
    });

    // Chặn reload trang khi nhấn Enter trong ô tìm kiếm
    if (searchForm) {
        searchForm.addEventListener("submit", (e) => {
            e.preventDefault();
            fetchAndRenderOrders();
        });
    }
});