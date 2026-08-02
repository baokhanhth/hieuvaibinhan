document.addEventListener("DOMContentLoaded", () => {
    // Dropdown elements
    const notifDropdown = document.querySelector(".notification-dropdown");
    const notifBtn = notifDropdown ? notifDropdown.querySelector(".notification-btn") : null;
    const notifMenu = notifDropdown ? notifDropdown.querySelector(".notification-menu") : null;

    const userDropdown = document.querySelector(".user-dropdown");
    const userBtn = userDropdown ? userDropdown.querySelector(".user-btn") : null;
    const userMenu = userDropdown ? userDropdown.querySelector(".dropdown-menu") : null;

    // Modal elements
    const modal = document.getElementById("change-pwd-modal");
    const btnOpenModal = document.getElementById("btn-open-change-pwd");
    const btnCloseModal = document.getElementById("btn-close-pwd-modal");
    const btnCancelModal = document.getElementById("btn-cancel-pwd-modal");
    const formChangePwd = document.getElementById("form-change-pwd");
    const alertMsg = document.getElementById("modal-alert-msg");

    // Notification dropdown toggle
    if (notifBtn && notifMenu) {
        notifBtn.addEventListener("click", (e) => {
            e.stopPropagation(); 
            const isOpening = !notifMenu.classList.contains("show");
            notifMenu.classList.toggle("show");
            if (userMenu) userMenu.classList.remove("show"); 

            if (isOpening) {
                const badge = notifBtn.querySelector(".notification-badge");
                if (badge) {
                    fetch("/accounts/notifications/mark-read/", {
                        method: "POST", 
                        headers: {
                            "X-Requested-With": "XMLHttpRequest",
                            "X-CSRFToken": getCsrfToken()
                        }
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            badge.remove();
                            notifMenu.querySelectorAll(".notification-item.unread").forEach(item => item.classList.remove("unread"));
                        }
                    })
                    .catch(err => console.error("Lỗi đánh dấu đã đọc:", err));
                }
            }
        });
    }

    // User dropdown toggle
    if (userBtn && userMenu) {
        userBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            userMenu.classList.toggle("show");
            if (notifMenu) notifMenu.classList.remove("show"); 
        });
    }

    if (notifMenu) notifMenu.addEventListener("click", (e) => e.stopPropagation());
    if (userMenu) userMenu.addEventListener("click", (e) => e.stopPropagation());

    document.addEventListener("click", () => {
        if (notifMenu) notifMenu.classList.remove("show");
        if (userMenu) userMenu.classList.remove("show");
    });

    // Helper Modal functions
    function openModal() {
        if (modal) {
            modal.style.display = "flex";
            if (userMenu) userMenu.classList.remove("show");
            if (alertMsg) alertMsg.style.display = "none";
            if (formChangePwd) formChangePwd.reset();
        }
    }

    function closeModal() {
        if (modal) {
            modal.style.display = "none";
        }
    }

    function showAlert(message, isError = true) {
        if (alertMsg) {
            alertMsg.className = `modal-alert ${isError ? 'error' : 'success'}`;
            alertMsg.textContent = message;
            alertMsg.style.display = "block";
        }
    }

    // Modal Event listeners
    if (btnOpenModal) {
        btnOpenModal.addEventListener("click", (e) => {
            e.preventDefault();
            openModal();
        });
    }

    if (btnCloseModal) btnCloseModal.addEventListener("click", closeModal);
    if (btnCancelModal) btnCancelModal.addEventListener("click", closeModal);

    // Bấm ra ngoài vùng trắng modal để đóng popup
    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) closeModal();
        });
    }

    // Form submission qua AJAX
    if (formChangePwd) {
        formChangePwd.addEventListener("submit", (e) => {
            e.preventDefault();

            const oldPwd = document.getElementById("swal-old-pwd").value.trim();
            const newPwd = document.getElementById("swal-new-pwd").value.trim();
            const confirmPwd = document.getElementById("swal-confirm-pwd").value.trim();

            if (!oldPwd || !newPwd || !confirmPwd) {
                showAlert("Vui lòng điền đầy đủ tất cả các trường.");
                return;
            }

            if (newPwd.length < 8) {
                showAlert("Mật khẩu mới phải có tối thiểu 8 ký tự.");
                return;
            }

            if (!/[A-Z]/.test(newPwd)) {
                showAlert("Mật khẩu mới phải có ít nhất 1 chữ hoa.");
                return;
            }

            if (!/\d/.test(newPwd)) {
                showAlert("Mật khẩu mới phải có ít nhất 1 chữ số.");
                return;
            }

            if (!/[!@#$%^&*(),.?":{}|<>]/.test(newPwd)) {
                showAlert("Mật khẩu mới phải có ít nhất 1 ký tự đặc biệt.");
                return;
            }

            if (newPwd !== confirmPwd) {
                showAlert("Mật khẩu xác nhận không khớp.");
                return;
            }

            const formData = new FormData(formChangePwd);

            fetch("/accounts/change-password/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken()
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message || "Đổi mật khẩu thành công!", false);
                    setTimeout(() => {
                        closeModal();
                    }, 1500);
                } else {
                    showAlert(data.message || "Đổi mật khẩu thất bại.");
                }
            })
            .catch(err => {
                showAlert("Có lỗi kết nối hệ thống. Vui lòng thử lại sau.");
                console.error("Change Password Error:", err);
            });
        });
    }
});

function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}