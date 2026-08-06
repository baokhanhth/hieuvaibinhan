const csrfToken = document.getElementById("csrf-token").value;

const btnDelete = document.getElementById("btn-delete-order");

function getHeaders() {
    return {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
    };
}

async function deleteOrder(orderId) {

    const result = await Swal.fire({
        icon: "warning",
        title: "Xóa hóa đơn?",
        html: `
            <div style="text-align:align">
                Hóa đơn sẽ được chuyển sang <b>Đã hủy</b>.
                Hoàn lại toàn bộ tồn kho.
                Trừ doanh thu của hóa đơn.
                Bạn có chắc chắn muốn tiếp tục?
            </div>
        `,
        showCancelButton: true,
        showCloseButton: true,
        confirmButtonText: "Xóa hóa đơn",
        cancelButtonText: "Hủy",
        confirmButtonColor: "#dc3545"
    });

    if (!result.isConfirmed) {
        return;
    }

    try {

        showLoading();

        const response = await fetch(
            `/sales/orders/${orderId}/delete/`,
            {
                method: "DELETE",
                headers: getHeaders()
            }
        );

        const data = await response.json();

        hideLoading();

        if (!data.success) {
            throw new Error(data.message);
        }

        await Swal.fire({
            icon: "success",
            title: "Thành công",
            text: data.message,
            timer: 1500,
            showConfirmButton: false,
            showCloseButton: true
        });

        window.location.href = "/sales/orders/list/";

    }
    catch (error) {

        hideLoading();

        Swal.fire({
            icon: "error",
            title: "Không thể xóa",
            text: error.message
        });

    }

}
function showLoading() {

    const overlay = document.getElementById("loading-overlay");

    if (overlay) {
        overlay.classList.remove("hidden");
    }

}

function hideLoading() {

    const overlay = document.getElementById("loading-overlay");

    if (overlay) {
        overlay.classList.add("hidden");
    }

}
document.addEventListener("DOMContentLoaded", function () {

    if (!btnDelete) {
        return;
    }

    btnDelete.addEventListener("click", function () {

        const orderId = this.dataset.id;

        deleteOrder(orderId);

    });

});