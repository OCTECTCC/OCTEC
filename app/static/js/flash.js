document.addEventListener('DOMContentLoaded', function () {
    var toast_elements = document.querySelectorAll('.toast');
    toast_elements.forEach(function (el) {
        var toast = new bootstrap.Toast(el);
        toast.show();
    });
});