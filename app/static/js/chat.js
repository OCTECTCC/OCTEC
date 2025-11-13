document.addEventListener("DOMContentLoaded", () => {
    let chat_selecionado = { tipo_chat: null, id_chat: null, descricao_chat: null }
    let timer = null
    let descricao_chat_selecionado = null
    let scroll_automatico = false
    
    const limite_scroll_automatico = 50 

    const mensagens_chat = document.getElementById("mensagens_chat")
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

    if (mensagens_chat) {
        mensagens_chat.addEventListener("scroll", () => {
            const proximo_baixo = (mensagens_chat.scrollTop + mensagens_chat.clientHeight) >= (mensagens_chat.scrollHeight - limite_scroll_automatico)
            scroll_automatico = proximo_baixo
        }, { passive: true })
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
        }

        if (descricao_chat_selecionado) {
            descricao_chat_selecionado.classList.remove("text-danger", "fw-bold")
            descricao_chat_selecionado = null
        }

        scroll_automatico = false
        ajustar_altura()
    }

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
        if (chat_selecionado.tipo_chat === tipo_chat && String(chat_selecionado.id_chat) === String(id_chat)) {
            return limpar_selecao()
        }

        chat_selecionado.tipo_chat = tipo_chat
        chat_selecionado.id_chat = id_chat
        chat_selecionado.descricao_chat = descricao_chat

        if (descricao_chat_clicado) {
            if (descricao_chat_selecionado && descricao_chat_selecionado !== descricao_chat_clicado) {
                descricao_chat_selecionado.classList.remove("text-danger", "fw-bold")
            }

            descricao_chat_clicado.classList.add("text-danger", "fw-bold")
            descricao_chat_selecionado = descricao_chat_clicado
        }

        if (chat_header) chat_header.classList.remove("d-none")
        if (chat_form) chat_form.classList.remove("d-none")

        titulo_chat.textContent = descricao_chat

        let pode_enviar = true
    
        if (tipo_chat === "canal" && descricao_chat_clicado) {
            const emissor_canal_str = descricao_chat_clicado.getAttribute("data-id-cargo-emissor")
            const emissor_canal_desc = descricao_chat_clicado.getAttribute("data-emissor-descricao") || "usuários autorizados"
            const emissor_canal = emissor_canal_str ? parseInt(emissor_canal_str, 10) : Infinity

            pode_enviar = (typeof cargo_usuario === "number" && !isNaN(cargo_usuario) && cargo_usuario >= emissor_canal)

            if (!pode_enviar) {
                input_chat.disabled = true
                enviar_chat.disabled = true
                input_chat.placeholder = `Você não possui permissão para mandar mensagem neste canal`
            } else {
                input_chat.disabled = false
                enviar_chat.disabled = false
                resetar_placeholder()
            }
        } else {
            input_chat.disabled = false
            enviar_chat.disabled = false
            resetar_placeholder()
        }

        if (!input_chat.disabled) input_chat.focus()

        scroll_automatico = true

        ajustar_altura()
        carregar_mensagens()

        if (timer) clearInterval(timer)
        timer = setInterval(carregar_mensagens, 1000)
    }

    async function carregar_mensagens() {
        if (!chat_selecionado.tipo_chat || !chat_selecionado.id_chat) return
        try {
            const busca = await fetch(`/api/mensagens?tipo_chat=${chat_selecionado.tipo_chat}&id_chat=${chat_selecionado.id_chat}`)
            if (!busca.ok) return
            const mensagens = await busca.json()
            exibir_mensagens(mensagens)
        } catch (erro) {
            console.error("Erro ao buscar mensagens:", erro)
        }
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

        mensagens.forEach(msg => {
            const sou_eu = mensagem_usuario_atual(msg.emissor_msg)

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
            const data_hora_msg = msg.data_hora_msg ? new Date(msg.data_hora_msg) : null
            const string_data_hora_msg = data_hora_msg ? data_hora_msg.toLocaleString("pt-BR") : ""

            const meta = document.createElement("div")
            meta.className = "mb-1 small fst-italic"

            if (sou_eu) {
                meta.classList.add("text-white-50")
                meta.style.textAlign = "right"
            } else {
                meta.classList.add("text-muted")
                meta.style.textAlign = "left"
            }

            meta.textContent = `${nome_usuario} • ${string_data_hora_msg}`

            const texto = document.createElement("div")
            texto.innerHTML = formatarHTML(msg.texto_msg)

            bubble.appendChild(meta)
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

    form_chat.addEventListener("submit", async (evento) => {
        evento.preventDefault()
        await enviar_mensagem()
    })

    input_chat.addEventListener("keydown", async (evento) => {
        if (evento.key === "Enter" && !evento.shiftKey) {
            evento.preventDefault()
            await enviar_mensagem()
        }
    })

    async function enviar_mensagem() {
        const texto_msg = input_chat.value.trim()

        if (!texto_msg || !chat_selecionado.tipo_chat || !chat_selecionado.id_chat) return

        enviar_chat.disabled = true

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
        }

        enviar_chat.disabled = false
        input_chat.focus()
    }

    function formatarHTML(texto_msg) {
        return texto_msg
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;")
    }

    ajustar_altura()
    limpar_selecao()
})