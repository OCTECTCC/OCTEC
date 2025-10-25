const header = document.getElementById("header")
const raiz = document.documentElement

function atualizar_altura_header() {
    const altura = header ? Math.ceil(header.getBoundingClientRect().height) : 0
    raiz.style.setProperty("--altura-header", altura + "px")
}

window.addEventListener("load", atualizar_altura_header, { once: true})
window.addEventListener("resize", atualizar_altura_header)

if (window.ResizeObserver && altura) {
    new ResizeObserver(atualizar_altura_header).observe(altura)
}
else if (altura && window.MutationObserver) {
    const mudanca = new MutationObserver(atualizar_altura_header)
    mudanca.observe(altura, { childList: true, subtree: true, attributes: true })
    setTimeout(atualizar_altura_header, 100)
}

document.querySelectorAll(".accordion").forEach(gaveta => {
    gaveta.addEventListener("shown.bs.collapse", atualizar_altura_header)
    gaveta.addEventListener("hidden.bs.collapse", atualizar_altura_header)
})