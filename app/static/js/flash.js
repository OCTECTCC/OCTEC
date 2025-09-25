document.addEventListener('DOMContentLoaded', function () {
    var toasts = document.querySelectorAll('.toast')
    toasts.forEach(function (el) {
        var toast = new bootstrap.Toast(el)
        toast.show()
    })
})