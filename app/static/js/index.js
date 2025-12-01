const header = document.getElementById("header")
const raiz = document.documentElement

function atualizar_altura_header() {
    const altura = header ? Math.ceil(header.getBoundingClientRect().height) : 0
    raiz.style.setProperty("--altura-header", altura + "px")
}

window.addEventListener("load", atualizar_altura_header, { once: true})
window.addEventListener("resize", atualizar_altura_header)

if (window.ResizeObserver && header) {
    new ResizeObserver(atualizar_altura_header).observe(header)
}
else if (header && window.MutationObserver) {
    const mudanca = new MutationObserver(atualizar_altura_header)
    mudanca.observe(header, { childList: true, subtree: true, attributes: true })
    setTimeout(atualizar_altura_header, 100)
}

document.querySelectorAll(".accordion").forEach(gaveta => {
    gaveta.addEventListener("shown.bs.collapse", atualizar_altura_header)
    gaveta.addEventListener("hidden.bs.collapse", atualizar_altura_header)
})

(function(){
  const loginUrl = document.body && document.body.dataset && document.body.dataset.loginUrl ? document.body.dataset.loginUrl : "/login"

  async function checkAuthAndRedirect() {
    try {
      const resp = await fetch("/api/some_ping", {
        method: "GET",
        cache: "no-store",
        credentials: "same-origin"
      })

      if (resp.status === 401 || resp.status === 403) {
        if (window.location.pathname !== new URL(loginUrl, window.location.origin).pathname) {
          window.location.href = loginUrl
        }
      }
    } catch (e) {}
  }

  window.addEventListener("load", checkAuthAndRedirect)

  window.addEventListener("pageshow", function(event) {
    checkAuthAndRedirect()
  })

  window.addEventListener("popstate", function() {
    checkAuthAndRedirect()
  })

  document.addEventListener("visibilitychange", function() {
    if (document.visibilityState === "visible") checkAuthAndRedirect()
  })

})()

window.addEventListener('pageshow', function(event) {
  if (event.persisted) {
    window.location.reload(true)
  }
})