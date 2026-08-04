document.addEventListener("DOMContentLoaded", () => {
    const notifBtn = document.getElementById("btn-toggle-notif");
    const notifMenu = document.getElementById("notif-menu-box");
    const userBtn = document.getElementById("btn-toggle-user");
    const userMenu = document.getElementById("user-menu-box");

    const btnOpenModal = document.getElementById("btn-open-change-pwd");
    const modalOverlay = document.getElementById("change-pwd-modal");
    const btnCloseModal = document.getElementById("btn-close-pwd-modal");
    const btnCancelModal = document.getElementById("btn-cancel-pwd-modal");
    const formChangePwd = document.getElementById("form-change-pwd");
    const alertMsg = document.getElementById("modal-alert-msg");

    function getCsrfToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

     if (notifBtn && notifMenu) {
        notifBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            notifMenu.classList.toggle("show");
            if (userMenu) userMenu.classList.remove("show");
        });
    }

    const btnMarkAllRead = document.getElementById("btn-mark-all-read");
    if (btnMarkAllRead && notifMenu) {
        btnMarkAllRead.addEventListener("click", (e) => {
            e.stopPropagation();
            const markReadUrl = notifMenu.dataset.markReadUrl || "/notifications/mark-read/";
            fetch(markReadUrl, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCsrfToken()
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const badge = notifBtn ? notifBtn.querySelector(".notification-badge") : null;
                    if (badge) badge.remove();
                    
                    notifMenu.querySelectorAll(".notification-item.unread").forEach(item => {
                        item.classList.remove("unread");
                    });
                    
                    btnMarkAllRead.style.display = "none";
                }
            })
            .catch(err => console.error("Lỗi đánh dấu đã đọc:", err));
        });
    }

    if (userBtn && userMenu) {
        userBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            userMenu.classList.toggle("show");
            if (notifMenu) notifMenu.classList.remove("show");
        });
    }

    document.addEventListener("click", () => {
        if (notifMenu) notifMenu.classList.remove("show");
        if (userMenu) userMenu.classList.remove("show");
    });

    if (notifMenu) notifMenu.addEventListener("click", (e) => e.stopPropagation());
    if (userMenu) userMenu.addEventListener("click", (e) => e.stopPropagation());

    function closeModal() {
        if (modalOverlay) {
            modalOverlay.style.display = "none";
            if (formChangePwd) formChangePwd.reset();
            if (alertMsg) alertMsg.style.display = "none";
        }
    }

    if (btnOpenModal) {
        btnOpenModal.addEventListener("click", (e) => {
            e.preventDefault();
            if (modalOverlay) {
                modalOverlay.style.display = "flex";
                if (userMenu) userMenu.classList.remove("show");
                if (alertMsg) alertMsg.style.display = "none";
                if (formChangePwd) formChangePwd.reset();
            }
        });
    }

    if (btnCloseModal) btnCloseModal.addEventListener("click", closeModal);
    if (btnCancelModal) btnCancelModal.addEventListener("click", closeModal);

    if (formChangePwd) {
        formChangePwd.addEventListener("submit", function (e) {
            e.preventDefault();

            const oldPwd = document.getElementById("swal-old-pwd").value;
            const newPwd = document.getElementById("swal-new-pwd").value;
            const confirmPwd = document.getElementById("swal-confirm-pwd").value;

            if (newPwd !== confirmPwd) {
                alertMsg.className = "modal-alert error";
                alertMsg.innerText = "Mật khẩu xác nhận không khớp.";
                alertMsg.style.display = "block";
                return;
            }

            const targetUrl = formChangePwd.getAttribute("action") || "/change-password/";

            const formData = new FormData();
            formData.append("old_password", oldPwd);
            formData.append("new_password", newPwd);
            formData.append("confirm_password", confirmPwd);

            fetch(targetUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken()
                },
                body: formData
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error("Mã lỗi HTTP: " + res.status);
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    alertMsg.className = "modal-alert success";
                    alertMsg.innerText = data.message;
                    alertMsg.style.display = "block";

                    setTimeout(() => {
                        closeModal();
                    }, 1500);
                } else {
                    alertMsg.className = "modal-alert error";
                    alertMsg.innerText = data.message || "Đổi mật khẩu thất bại.";
                    alertMsg.style.display = "block";
                }
            })
            .catch(err => {
                alertMsg.className = "modal-alert error";
                alertMsg.innerText = "Lỗi kết nối server (404/500). Vui lòng kiểm tra lại URL trong urls.py.";
                alertMsg.style.display = "block";
            });
        });
    }
});