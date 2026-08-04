document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("searchForm");

    const searchInput = document.getElementById("q");

    const status = document.getElementById("status");

    let timer;

    searchInput.addEventListener("input", () => {

        clearTimeout(timer);

        timer = setTimeout(() => {

            form.submit();

        },300);

    });

    status.addEventListener("change", () => {

        form.submit();

    });

});