document.addEventListener("DOMContentLoaded", () => {
    const notifDropdown = document.querySelector(".notification-dropdown");
    const notifBtn = notifDropdown ? notifDropdown.querySelector(".notification-btn") : null;
    const notifMenu = notifDropdown ? notifDropdown.querySelector(".notification-menu") : null;

    const userDropdown = document.querySelector(".user-dropdown");
    const userBtn = userDropdown ? userDropdown.querySelector(".user-btn") : null;
    const userMenu = userDropdown ? userDropdown.querySelector(".dropdown-menu") : null;

    if (notifBtn && notifMenu) {
        notifBtn.addEventListener("click", (e) => {
            e.stopPropagation(); 
            notifMenu.classList.toggle("show");
            if (userMenu) userMenu.classList.remove("show"); 
        });
    }

    if (userBtn && userMenu) {
        userBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            userMenu.classList.toggle("show");
            if (notifMenu) notifMenu.classList.remove("show"); 
        });
    }

    if (notifMenu) {
        notifMenu.addEventListener("click", (e) => {
            e.stopPropagation();
        });
    }
    if (userMenu) {
        userMenu.addEventListener("click", (e) => {
            e.stopPropagation();
        });
    }

    document.addEventListener("click", () => {
        if (notifMenu) notifMenu.classList.remove("show");
        if (userMenu) userMenu.classList.remove("show");
    });
});