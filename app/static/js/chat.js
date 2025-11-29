document.addEventListener("DOMContentLoaded", () => {
    const mensagens_chat = document.getElementById("mensagens_chat")

    if (!mensagens_chat) return

    let chat_selecionado = { tipo_chat: null, id_chat: null, descricao_chat: null }
    let timer = null
    let descricao_chat_selecionado = null
    let scroll_automatico = false
    
    const limite_scroll_automatico = 50 

    const input_chat = document.getElementById("input_chat")
    const enviar_chat = document.getElementById("enviar_chat")
    const form_chat = document.getElementById("form_chat")
    const titulo_chat = document.getElementById("titulo_chat")

    const chat_header = document.getElementById("chat_header")
    const chat_form = document.getElementById("chat_form")

    const cargo_usuario = mensagens_chat ? parseInt(mensagens_chat.dataset.cargoUsuario, 10) : null

    const placeholder_padrao = "Escreva uma mensagem"

    function resetar_placeholder() {
        if (input_chat) input_chat.placeholder = placeholder_padrao
    }

    const usuario_atual_bruto = mensagens_chat ? mensagens_chat.dataset.currentUser : null

    function converter_usuario_atual(usuario_atual_bruto) {
        if (!usuario_atual_bruto) return { tipo_usuario: null, id_usuario: null }

        if (usuario_atual_bruto.includes("-")) {
            const [tipo_usuario, id_usuario] = usuario_atual_bruto.split("-", 2)
            return { tipo_usuario: String(tipo_usuario), id_usuario: String(id_usuario) }
        }

        return { tipo_usuario: null, id_usuario: String(usuario_atual_bruto) }
    }
    const usuario_atual = converter_usuario_atual(usuario_atual_bruto)

    function mensagem_usuario_atual(emissor_msg) {
        if (!emissor_msg) return false

        const tipo_emissor = emissor_msg.tipo_usuario ? String (emissor_msg.tipo_usuario) : null
        const id_emissor = (emissor_msg.id_usuario !== undefined && emissor_msg.id_usuario !== null) ? String(emissor_msg.id_usuario) : null

        if (usuario_atual.tipo_usuario) {
            return tipo_emissor === usuario_atual.tipo_usuario && id_emissor === usuario_atual.id_usuario
        }

        if (usuario_atual.id_usuario) {
            return id_emissor === usuario_atual.id_usuario
        }

        return false
    }

    function ajustar_altura() {
        if (!mensagens_chat) return

        const chat_header_visivel = chat_header && !chat_header.classList.contains("d-none")
        const chat_form_visivel = chat_form && !chat_form.classList.contains("d-none")

        const offset_cima = chat_header_visivel ? chat_header.offsetHeight : 0
        const offset_baixo = chat_form_visivel ? chat_form.offsetHeight : 0

        const desvio = 8

        mensagens_chat.style.top = offset_cima + "px"
        mensagens_chat.style.bottom = (offset_baixo + desvio) + "px"
    }

    window.addEventListener("resize", ajustar_altura)

    mensagens_chat.addEventListener("scroll", () => {
        const proximo_baixo = (mensagens_chat.scrollTop + mensagens_chat.clientHeight) >= (mensagens_chat.scrollHeight - limite_scroll_automatico)
        scroll_automatico = proximo_baixo
    }, { passive: true })

    function abortar_chat_fetch() {
        try {
            if (mensagens_chat && mensagens_chat._fetchController) {
                mensagens_chat._fetchController.abort();
            }
        } catch (error) {
            console.error("Erro abortando fetch do chat:", error);
        } finally {
            if (mensagens_chat) mensagens_chat._fetchController = null;
        }
    }

    function limpar_selecao() {
        chat_selecionado = { tipo_chat: null, id_chat: null, descricao_chat: null }

        if (timer) {
            clearInterval(timer)
            timer = null
        }

        if (chat_header) chat_header.classList.add("d-none")
        if (chat_form) chat_form.classList.add("d-none")
        if (titulo_chat) titulo_chat.textContent = ""

        if (input_chat) {
            input_chat.value = ""
            input_chat.disabled = true
            input_chat.placeholder = placeholder_padrao
        }

        if (enviar_chat) enviar_chat.disabled = true

        if (mensagens_chat) {
            mensagens_chat.className = "d-flex justify-content-center align-items-center position-absolute start-0 end-0 overflow-auto p-2 no-scrollbar"
            mensagens_chat.innerText = "Selecione um canal"
            mensagens_chat.dataset.view = ""
        }

        if (descricao_chat_selecionado) {
            descricao_chat_selecionado.classList.remove("text-danger", "fw-bold")
            descricao_chat_selecionado = null
        }

        abortar_chat_fetch();
        scroll_automatico = false
        ajustar_altura()
    }

    document.addEventListener("limpar_sessao_chat", () => {
        try {
            limpar_selecao()
        } catch (e) {
            console.error("Erro ao tentar limpar seleção do chat via evento:", e)
        }
    })

    document.querySelectorAll("[data-canal]").forEach(elemento => {
        elemento.addEventListener("click", (evento) => {
            evento.preventDefault()
            const id_chat = elemento.getAttribute("data-canal")
            const descricao_chat = elemento.getAttribute("data-descricao-canal") || elemento.textContent.trim()
            selecionar_chat("canal", id_chat, descricao_chat, elemento)
        })
    })

    document.querySelectorAll("[data-aula]").forEach(elemento => {
        elemento.addEventListener("click", (evento) => {
            evento.preventDefault()
            const id_chat = elemento.getAttribute("data-aula")
            const descricao_chat = elemento.getAttribute("data-descricao-aula") || elemento.textContent.trim()
            selecionar_chat("aula", id_chat, descricao_chat, elemento)
        })
    })

    function selecionar_chat(tipo_chat, id_chat, descricao_chat, descricao_chat_clicado = null) {
        try {
            document.dispatchEvent(new Event("limpar_sessao_solicitacoes"))
        } catch (error) {
            console.error("Erro ao dispatch limpar_sessao_solicitacoes:", error)
        }

        if (chat_selecionado.tipo_chat === tipo_chat && String(chat_selecionado.id_chat) === String(id_chat)) {
            return limpar_selecao()
        }

        const _tipo_chat = tipo_chat
        const _id_chat = id_chat
        const _descricao_chat = descricao_chat
        const _descricao_chat_clicado = descricao_chat_clicado

        setTimeout(() => {
            if (mensagens_chat) mensagens_chat.dataset.view = "chat"

            chat_selecionado.tipo_chat = _tipo_chat
            chat_selecionado.id_chat = _id_chat
            chat_selecionado.descricao_chat = _descricao_chat

            if (_descricao_chat_clicado) {
                if (descricao_chat_selecionado && descricao_chat_selecionado !== _descricao_chat_clicado) {
                    descricao_chat_selecionado.classList.remove("text-danger", "fw-bold")
                }

                _descricao_chat_clicado.classList.add("text-danger", "fw-bold")
                descricao_chat_selecionado = _descricao_chat_clicado
            }

            if (chat_header) chat_header.classList.remove("d-none")
            if (chat_form) chat_form.classList.remove("d-none")

            if (titulo_chat) titulo_chat.textContent = _descricao_chat

            let pode_enviar = true

            if (_tipo_chat === "canal" && _descricao_chat_clicado) {
                const emissor_canal_str = _descricao_chat_clicado.getAttribute("data-id-cargo-emissor")
                const moderador_canal_str = _descricao_chat_clicado.getAttribute("data-id-cargo-moderador")

                let emissor_cargo = null
                let moderador_cargo = null

                if (emissor_canal_str) emissor_cargo = parseInt(emissor_canal_str, 10)

                if (emissor_cargo !== null) {
                    pode_enviar = (typeof cargo_usuario === "number" && !isNaN(cargo_usuario) && cargo_usuario >= emissor_cargo)
                } else {
                    pode_enviar = true
                }

                if (!pode_enviar && moderador_cargo !== null && cargo_usuario === moderador_cargo) {
                    pode_enviar = true
                }

                if (!pode_enviar) {
                    if (input_chat) {
                        input_chat.disabled = true
                        input_chat.placeholder = "Você não possui permissão para mandar mensagem neste canal"
                    }

                    if (enviar_chat) enviar_chat.disabled = true
                } else {
                    if (input_chat) {
                        input_chat.disabled = false
                        resetar_placeholder()
                    }
                    
                    if (enviar_chat) enviar_chat.disabled = false
                }
            } else {
                if (input_chat) input_chat.disabled = false
                if (enviar_chat) enviar_chat.disabled = false
                resetar_placeholder()
            }

            if (input_chat && !input_chat.disabled) input_chat.focus()

            scroll_automatico = true

            ajustar_altura()
            carregar_mensagens()

            if (timer) clearInterval(timer)

            timer = setInterval(() => {
                if (mensagens_chat && mensagens_chat.dataset.view === "chat") {
                    carregar_mensagens()
                }
            }, 1000)
        }, 0)
    }

    async function carregar_mensagens() {
        if (!chat_selecionado.tipo_chat || !chat_selecionado.id_chat) return

        if (!mensagens_chat || mensagens_chat.dataset.view !== "chat") return

        abortar_chat_fetch()

        const controller = new AbortController()

        if (mensagens_chat) mensagens_chat._fetchController = controller

        try {
            const url = `/api/mensagens?tipo_chat=${encodeURIComponent(chat_selecionado.tipo_chat)}&id_chat=${encodeURIComponent(chat_selecionado.id_chat)}`
            const resp = await fetch(url, { signal: controller.signal })

            if (!resp.ok) {
                console.error("Erro ao buscar mensagens:", resp.status)
                return
            }

            const mensagens = await resp.json()

            if (!mensagens_chat || mensagens_chat.dataset.view !== "chat") return
            
            exibir_mensagens(mensagens)
        } catch (error) {
            if (error && error.name === "AbortError") return
            console.error("Erro ao buscar mensagens:", error)
        } finally {
            if (mensagens_chat) mensagens_chat._fetchController = null
        }
    }

    function mostrar_toast(mensagem, tipo = "success") {
        const container = document.createElement("div")
        container.className = "position-fixed bottom-0 end-0 p-3 z-3"

        const toast = document.createElement("div")
        toast.className = `toast align-items-center text-bg-${tipo} border-0`
        toast.setAttribute("role", "status")

        const inner = document.createElement("div")
        inner.className = "d-flex"

        const body = document.createElement("div")
        body.className = "toast-body"
        body.textContent = mensagem

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

        const bs_toast = new bootstrap.Toast(toast, { delay: 4000 })
        bs_toast.show()

        toast.addEventListener("hidden.bs.toast", () => container.remove())
    }


    function exibir_mensagens(mensagens) {
        mensagens_chat.innerHTML = ""
        mensagens_chat.className = "position-absolute start-0 end-0 overflow-auto p-2 no-scrollbar"

        if (!Array.isArray(mensagens) || mensagens.length === 0) {
            mensagens_chat.className = "d-flex justify-content-center align-items-center position-absolute start-0 end-0 overflow-auto p-2 no-scrollbar"
            mensagens_chat.innerText = "Nenhuma mensagem ainda"
            ajustar_altura()
            return
        }

        const cargo_atual = (typeof cargo_usuario === "number" && !isNaN(cargo_usuario)) ? cargo_usuario : null
        const eu_representante = mensagens_chat.dataset.representante === "true" || mensagens_chat.dataset.representante === true

        mensagens.forEach(msg => {
            const sou_eu = mensagem_usuario_atual(msg.emissor_msg)
            const emissor = msg.emissor_msg || {}
            const emissor_tipo = emissor.tipo_usuario || null
            const emissor_representante = !!emissor.representante

            let pode_deletar = false

            if (sou_eu) {
                pode_deletar = true
            } else {
                if (chat_selecionado.tipo_chat === "aula" || chat_selecionado.tipo_chat === "canal") {
                    if (cargo_atual === 1) {
                        if (eu_representante && emissor_tipo === "aluno" && emissor_representante === false) {
                            pode_deletar = true
                        }
                    } else if (cargo_atual === 3) {
                        if (emissor_tipo === "aluno") pode_deletar = true
                    } else if (cargo_atual === 4) {
                        if (emissor_tipo === "aluno" || emissor_tipo === "prof") pode_deletar = true
                    } else if (cargo_atual === 5) {
                        pode_deletar = true
                    }
                }
            }

            const row = document.createElement("div")
            row.classList.add("d-flex", "w-100", "mb-2")
            row.classList.add(sou_eu ? "justify-content-end" : "justify-content-start")

            const bubble = document.createElement("div")
            bubble.classList.add("p-2", "rounded", "d-inline-block")

            if (sou_eu) {
                bubble.classList.add("text-bg-danger", "text-light", "text-start")
            } else {
                bubble.classList.add("bg-light", "text-dark", "text-start")
            }

            bubble.style.maxWidth = "80%"
            bubble.style.overflowWrap = "break-word"
            bubble.style.wordBreak = "break-word"

            const nome_usuario = (msg.emissor_msg && msg.emissor_msg.nome_usuario) ? msg.emissor_msg.nome_usuario : "Usuário"
            const rotulo_emissor = (msg.emissor_msg && msg.emissor_msg.rotulo_emissor) ? msg.emissor_msg.rotulo_emissor : null
            const data_hora_msg = msg.data_hora_msg ? new Date(msg.data_hora_msg) : null
            const string_data_hora_msg = data_hora_msg ? data_hora_msg.toLocaleString("pt-BR") : ""

            const top_container = document.createElement("div")
            top_container.className = "d-flex justify-content-between align-items-center mb-1"

            const meta = document.createElement("div")
            meta.className = "small fst-italic"

            if (sou_eu) {
                meta.classList.add("text-white-50")
                meta.style.textAlign = "left"
            } else {
                meta.classList.add("text-muted")
                meta.style.textAlign = "left"
            }

            const label = rotulo_emissor || nome_usuario

            meta.textContent = `${label} • ${string_data_hora_msg}`

            top_container.appendChild(meta)

            if (pode_deletar) {
                const btn_exluir = document.createElement("button")
                btn_exluir.title = "Excluir mensagem"
                btn_exluir.type = "button"
                btn_exluir.style.minWidth = "36px"
                btn_exluir.dataset.idMsg = msg.id_msg
                btn_exluir.tabIndex = 0

                if (sou_eu) {
                    btn_exluir.className = "btn btn-sm btn-danger ms-2"
                    btn_exluir.innerHTML = '<i class="bi bi-trash-fill text-white"></i>'
                } else {
                    btn_exluir.className = "btn btn-sm ms-2"
                    btn_exluir.style.background = "transparent"
                    btn_exluir.style.border = "none"
                    btn_exluir.style.padding = "0.25rem 0.45rem"
                    btn_exluir.innerHTML = '<i class="bi bi-trash-fill text-danger"></i>'
                }

                btn_exluir.addEventListener("click", async () => {
                    const confirm_label = rotulo_emissor || nome_usuario || "esta mensagem"

                    if (!confirm(`Excluir mensagem de ${confirm_label}?`)) return

                    btn_exluir.disabled = true

                    try {
                        const resp = await fetch("/api/mensagens/excluir", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ id_msg: msg.id_msg })
                        })

                        let json = null

                        try {
                            json = await resp.clone().json()
                        } catch (error) {
                            json = null
                        }

                        if (!resp.ok) {
                            const mensagem_erro = (json && json.error) ? json.error : "Erro ao excluir mensagem"
                            console.error("Erro excluir:", resp.status, json)
                            mostrar_toast(mensagem_erro, "danger")
                            btn_exluir.disabled = false
                            return
                        }

                        row.remove()

                        mostrar_toast("Mensagem excluída", "success")
                    } catch (erro) {
                        console.error("Erro fetch excluir:", erro)
                        mostrar_toast("Erro de rede ao excluir mensagem", "danger")
                        btn_exluir.disabled = false
                    }
                })

                top_container.appendChild(btn_exluir)
            }  

            const texto = document.createElement("div")
            texto.innerHTML = formatarHTML(msg.texto_msg)

            bubble.appendChild(top_container)
            bubble.appendChild(texto)
            row.appendChild(bubble)
            mensagens_chat.appendChild(row)
        })

        ajustar_altura()

        if (scroll_automatico) {
            requestAnimationFrame(() => {
                const scroll_maximo = mensagens_chat.scrollHeight - mensagens_chat.clientHeight
                mensagens_chat.scrollTop = scroll_maximo > 0 ? scroll_maximo : 0
            })
        }
    }

    if (form_chat) {
        form_chat.addEventListener("submit", async (evento) => {
            evento.preventDefault()
            await enviar_mensagem()
        })
    }

    if (input_chat) {
        input_chat.addEventListener("keydown", async (evento) => {
            if (evento.key === "Enter" && !evento.shiftKey) {
                evento.preventDefault()
                await enviar_mensagem()
            }
        })
    }

    async function enviar_mensagem() {
        if (!input_chat) return

        const texto_msg = input_chat.value.trim()

        if (!texto_msg || !chat_selecionado.tipo_chat || !chat_selecionado.id_chat) return

        if (enviar_chat) enviar_chat.disabled = true

        try {
            const busca = await fetch("/api/mensagens/enviar", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ texto_msg: texto_msg, tipo_chat: chat_selecionado.tipo_chat, id_chat: chat_selecionado.id_chat})
            })
            const resposta = await busca.json()

            if (!busca.ok) {
                console.error("Erro envio:", resposta)
                alert(resposta.error || "Erro ao enviar mensagem")
            } else {
                input_chat.value = ""
                carregar_mensagens()
            }
        } catch (erro) {
            console.error("Erro ao enviar:", erro)
        } finally {
            if (enviar_chat) enviar_chat.disabled = false

            if (input_chat) input_chat.focus()
        }

        enviar_chat.disabled = false
        input_chat.focus()
    }

    function formatarHTML(texto_msg) {
        return String(texto_msg || "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;")
    }

    ajustar_altura()
    limpar_selecao()
})