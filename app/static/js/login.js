document.addEventListener('DOMContentLoaded', function () {
    const tipo_usuario = document.getElementById('select_usuario')
    let tipo_usuario_anterior = tipo_usuario.value
    const login_label = document.querySelector('label[for="input_login"]')
    const login_input = document.getElementById('input_login')
    const etec_input = document.getElementById('input_etec')
    const senha_input = document.getElementById('input_senha')

    function limpar_campos() {
        if (login_input) login_input.value = ""
        if (etec_input) etec_input.value = ""
        if (senha_input) senha_input.value = ""
    }

    function atualizar_login() {
        const opcao = tipo_usuario.options[tipo_usuario.selectedIndex]
        const texto_opcao = opcao ? opcao.text : ''

        if (tipo_usuario.value !== tipo_usuario_anterior) {
            limpar_campos()
        }

        tipo_usuario_anterior = tipo_usuario.value

        if (texto_opcao.includes('Aluno')) {
            login_label.textContent = 'RM'
            login_input.placeholder = 'Digite seu RM'
            login_input.minLength = 5
            login_input.maxLength = 6
            login_input.pattern = "\\d{5,6}"
        }
        else {
            login_label.textContent = 'Login'
            login_input.placeholder = 'Digite seu login'
            login_input.removeAttribute("minLength")
            login_input.removeAttribute("maxLength")
            login_input.removeAttribute("pattern")
        }
    }

    if (tipo_usuario) {
        tipo_usuario.addEventListener('change', atualizar_login)
    }

    atualizar_login()

    function mostrar_toast(texto, tipo = "success") {
        const container = document.createElement("div")
        container.className = "position-fixed bottom-0 end-0 p-3 z-3"
        
        const toast = document.createElement("div")
        toast.className = `toast align-items-center text-bg-${tipo} border-0`
        toast.setAttribute("role", "status")

        const inner = document.createElement("div")
        inner.className = "d-flex"

        const body = document.createElement("div")
        body.className = "toast-body"
        body.textContent = texto
        
        const btn = document.createElement("button")
        btn.className = "btn-close btn-close-white me-2 m-auto"
        btn.type = "button"
        btn.addEventListener("click", () => {
            const bs = bootstrap.Toast.getInstance(toast)
            if (bs) bs.hide()
        })

        inner.appendChild(body)
        inner.appendChild(btn)
        toast.appendChild(inner)
        container.appendChild(toast)
        document.body.appendChild(container)

        const bsToast = new bootstrap.Toast(toast, { delay: 5000 })
        bsToast.show()
        toast.addEventListener("hidden.bs.toast", () => container.remove())
    }

    async function solicitarRedefinicao(event) {
        event.preventDefault()
        const tipo = document.getElementById('select_usuario').value
        const etec = document.getElementById('input_etec').value.trim()
        const login = document.getElementById('input_login').value.trim()

        if (!tipo) { mostrar_toast("Selecione o tipo de usuário", "warning"); return }
        if (!etec || etec.length !== 3) { mostrar_toast("Informe o código da ETEC (3 dígitos)", "warning"); return }
        if (!login) { mostrar_toast("Informe seu login / RM", "warning"); return }

        if (!confirm("Deseja solicitar a redefinição de senha com esses dados?")) return

        try {
            const resp = await fetch("/api/solicitacoes/solicitar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tipo_usuario: tipo, etec_usuario: etec, login_usuario: login })
            })

            let json = {}
            try { json = await resp.json() } catch(e){}

            if (resp.status === 201) {
                mostrar_toast("Solicitação criada com sucesso", "success")
            } else if (resp.status === 409) {
                mostrar_toast(json.error || "Já existe uma solicitação pendente", "warning")
            } else {
                mostrar_toast(json.error || "Erro ao criar solicitação", "danger")
            }
        } catch (err) {
            console.error(err)
            mostrar_toast("Erro de rede ao enviar solicitação", "danger")
        }
    }

    const linkSolicitar = document.getElementById('link_solicitar_redefinicao')
    if (linkSolicitar) linkSolicitar.addEventListener('click', solicitarRedefinicao)
})