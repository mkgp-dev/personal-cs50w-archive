$(document).ready(function () {
    $(document).on('click', '.feeling-lucky', function () {
        const q = $(".user-query").val();

        if (q) {
            window.location.href = `https://www.google.com/search?q=${encodeURIComponent(q)}&btnI=1`;
        } else {
            window.location.href = 'https://doodles.google/';
        }
    });

    $(document).on('click', '.image-search', function () {
        window.location.href = './image.html';
    });

    $(document).on('click', '.advance-search', function () {
        window.location.href = './advance.html';
    });

    $(document).on('click', '.google-search', function () {
        window.location.href = './index.html';
    });
});