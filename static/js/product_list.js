document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("searchForm");
    const searchInput = document.getElementById("q");
    const statusSelect = document.getElementById("status");

    let timer;

    if (searchInput) {
        searchInput.addEventListener("input", () => {
            clearTimeout(timer);
            timer = setTimeout(() => {
                form.submit();
            }, 300);
        });
    }

    if (statusSelect) {
        statusSelect.addEventListener("change", () => {
            form.submit();
        });
    }
});