document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("searchForm");
    const input = document.getElementById("q");

    if (!form || !input) return;

    let timer;

    input.addEventListener("input", () => {

        clearTimeout(timer);

        timer = setTimeout(() => {
            form.submit();
        }, 300);

    });

});