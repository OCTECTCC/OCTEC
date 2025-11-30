document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-color]').forEach(function(el){
        var color = el.dataset.color || '#6c757d'
        if (/^#[0-9A-Fa-f]{6}$/.test(color)) {
            el.style.backgroundColor = color
        } else {
            el.style.backgroundColor = '#6c757d'
        }
    })
})