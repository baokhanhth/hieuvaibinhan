document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("searchForm");
    const input = document.getElementById("q");
    const status = document.getElementById("statusFilter");

    if (!form) return;

    let timer;

    function submitForm() {
        clearTimeout(timer);

        timer = setTimeout(() => {
            form.submit();
        }, 300);
    }

    if (input) {
        input.addEventListener("input", submitForm);
    }

    if (status) {
        status.addEventListener("change", () => {
            form.submit();
        });
    }

});