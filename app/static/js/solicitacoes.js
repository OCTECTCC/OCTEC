document.addEventListener("DOMContentLoaded", () => {
        const solicitacoes_canal = document.getElementById("mensagens_chat")

        if (!solicitacoes_canal) return

        const cargo_usuario = solicitacoes_canal.dataset.cargoUsuario ? parseInt(solicitacoes_canal.dataset.cargoUsuario, 10) : null

        if (cargo_usuario !== 2) {
                solicitacoes_canal.className = "d-flex justify-content-center align-items-center position-absolute start-0 end-0 overflow-auto p-2 no-scrollbar"
                solicitacoes_canal.innerText = "Selecione um canal"
                return
        }

        const canal_header = document.getElementById("chat_header")
        const canal_form = document.getElementById("chat_form")
        const titulo_canal = document.getElementById("titulo_chat")

        let canal_selecionado = null
        let descricao_canal_selecionado = null

        function limpar_canal() {
                if (canal_header) canal_header.classList.add("d-none")

                if (canal_form) canal_form.classList.add("d-none")

                if (titulo_canal) titulo_canal.textContent = ""

                if (solicitacoes_canal) {
                        solicitacoes_canal.className = "d-flex justify-content-center align-items-center position-absolute start-0 end-0 overflow-auto p-2 no-scrollbar"
                        solicitacoes_canal.innerText = "Selecione uma categoria de solicitações"
                }
                
                if (descricao_canal_selecionado) {
                        descricao_canal_selecionado.classList.remove("text-danger", "fw-bold")
                        descricao_canal_selecionado = null
                }
        }

        function mostrar_toast(mensagem, tipo = "success") {
                const container = document.createElement("div")
                container.className = "position-fixed bottom-0 end-0 p-3 z-3"

                const toast = document.createElement("div")
                toast.className = `toast align-items-center text-bg-${tipo} border-0`
                toast.setAttribute("role", "status")

                const toast_inner = document.createElement("div")
                toast_inner.className = "d-flex"

                const toast_body = document.createElement("div")
                toast_body.className = "toast-body"
                toast_body.textContent = mensagem

                const toast_botao = document.createElement("button")
                toast_botao.className = "btn-close btn-close-white me-2 m-auto"
                toast_botao.type = "button"
                toast_botao.addEventListener("click", () => {
                        const bs = bootstrap.Toast.getInstance(toast)
                        if (bs) bs.hide()
                })

                toast_inner.appendChild(toast_body)
                toast_inner.appendChild(toast_botao)
                toast.appendChild(toast_inner)
                container.appendChild(toast)
                document.body.appendChild(container)

                const bootstrap_toast = new bootstrap.Toast(toast, { delay: 4000 })

                bootstrap_toast.show()

                toast.addEventListener("hidden.bs.toast", () => container.remove())
        }

        function formatarHTML(texto_msg) {
                return texto_msg
                        .replaceAll("&", "&amp;")
                        .replaceAll("<", "&lt;")
                        .replaceAll(">", "&gt;")
                        .replaceAll('"', "&quot;")
                        .replaceAll("'", "&#039;")
        }

        function montar_solicitacao(solicitacao) {
                const row = document.createElement("div")
                row.className = "d-flex justify-content-start w-100 mb-2"

                const bubble = document.createElement("div")
                bubble.className = "p-2 rounded d-inline-block bg-light text-dark text-start"
                bubble.style.maxWidth = "90%"
                bubble.style.wordBreak = "break-word"
                bubble.style.overflowWrap = "break-word"

                const meta = document.createElement("div")
                meta.className = "mb-1 small fst-italic text-muted"

                const label = solicitacao.rotulo_emissor || solicitacao.nome_usuario || "Usuário"
                const dataStr = solicitacao.data_hora_solict ? new Date(solicitacao.data_hora_solict).toLocaleString("pt-BR") : ""
                meta.textContent = `${label} • ${dataStr}`

                const texto = document.createElement("div")
                texto.className = "mb-2"
                texto.innerHTML = `Solicitação de redefinição de senha.`

                const botao_redefinir = document.createElement("button")
                botao_redefinir.className = "btn btn-sm btn-danger"
                botao_redefinir.textContent = "Redefinir"
                botao_redefinir.dataset.idSolict = solicitacao.id_solict
                botao_redefinir.dataset.tipo = solicitacao.tipo

                botao_redefinir.addEventListener("click", async () => {
                        const confirmLabel = solicitacao.rotulo_emissor || solicitacao.nome_usuario || "este usuário"

                        if (!confirm(`Redefinir senha de ${confirmLabel}?`)) return

                        botao_redefinir.disabled = true

                        try {
                                const resposta = await fetch("/api/solicitacoes/redefinir", {
                                        method: "POST",
                                        headers: { "Content-Type": "application/json" },
                                        body: JSON.stringify({ id_solict: solicitacao.id_solict, tipo: solicitacao.tipo })
                                })

                                let json = null

                                try {
                                        json = await resposta.clone().json()
                                } catch (erro) {
                                        try { 
                                                json = await resposta.clone().text()
                                        } catch (erro2) {
                                                json = null
                                        }
                                }

                                if (!resposta.ok) {
                                        const mensagem = (json && json.error) ? json.error : (typeof json === "string" ? json : "Erro ao redefinir")
                                        console.error("Resposta inválida:", resposta.status, json)
                                        mostrar_toast(mensagem, "danger")
                                        botao_redefinir.disabled = false
                                        return
                                }

                                row.remove()

                                mostrar_toast("Senha redefinida com sucesso", "success")
                        } catch (erro) {
                                console.error("Erro fetch:", erro)
                                mostrar_toast("Erro de rede" + (erro && erro.message ? erro.message : ""), "danger")
                                botao_redefinir.disabled = false
                        }
                })

                bubble.appendChild(meta)
                bubble.appendChild(texto)
                bubble.appendChild(botao_redefinir)
                row.appendChild(bubble)

                return row
        }

        async function carregar_solicitacoes(canal) {
                if (!canal) return

                try {
                        const resposta = await fetch(`/api/solicitacoes?canal=${encodeURIComponent(canal)}`)

                        if (!resposta.ok) {
                                mostrar_toast("Erro ao buscar solicitações", "danger")
                                return
                        }

                        const lista = await resposta.json()

                        solicitacoes_canal.innerHTML = ""
                        solicitacoes_canal.className = "position-absolute start-0 end-0 overflow-auto p-2 no-scrollbar"

                        if (!Array.isArray(lista) || lista.length === 0) {
                                solicitacoes_canal.className = "d-flex justify-content-center align-items-center position-absolute start-0 end-0 overflow-auto p-2 no-scrollbar"
                                solicitacoes_canal.innerText = "Nenhuma solicitação"
                                return
                        }

                        lista.forEach(solicitacao => {
                                const bubble = montar_solicitacao(solicitacao)
                                solicitacoes_canal.appendChild(bubble)
                        })

                        requestAnimationFrame(() => {
                                solicitacoes_canal.scrollTop = solicitacoes_canal.scrollHeight
                        })
                } catch (erro) {
                        console.error(erro)
                        mostrar_toast("Erro de rede ao buscar solicitações", "danger")
                }
        }

        document.querySelectorAll("[data-solicitacoes-canal]").forEach(elemento => {
                elemento.addEventListener("click", (evento) => {
                        evento.preventDefault()

                        const canal = elemento.dataset.solicitacoesCanal

                        if (canal_selecionado === canal) {
                                canal_selecionado = null
                                limpar_canal()
                                return
                        }

                        canal_selecionado = canal

                        if (descricao_canal_selecionado && descricao_canal_selecionado !== elemento) {
                                descricao_canal_selecionado.classList.remove("text-danger", "fw-bold")
                        }

                        elemento.classList.add("text-danger", "fw-bold")
                        descricao_canal_selecionado = elemento

                        if (canal_header) canal_header.classList.remove("d-none")
                        if (canal_form) canal_form.classList.add("d-none")
                        if (titulo_canal) titulo_canal.textContent = `Solicitações — ${elemento.textContent.trim()}`

                        carregar_solicitacoes(canal)
                })
        })

        limpar_canal()
})