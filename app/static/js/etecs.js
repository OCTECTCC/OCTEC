document.addEventListener('DOMContentLoaded', function () {
    const select_cidade = document.getElementById('select_cidade')
    const select_etec = document.getElementById('select_etec')
    const button_etec = document.getElementById('button_etec')
    const input_etec = document.getElementById('input_etec')
    const div_modal_etec = document.getElementById('div_modal_etec')

    function instanciar_modal() {
        return bootstrap.Modal.getInstance(div_modal_etec) || new bootstrap.Modal(div_modal_etec)
    }

    async function etecs_por_cidade(id_cidade) {
        select_etec.innerHTML = '<option value="" selected disabled>Carregando...</option>'

        try {
            const resposta = await fetch(`/api/etecs?cidade=${encodeURIComponent(id_cidade)}`)

            if (!resposta.ok) throw new Error('Erro ao buscar ETECs')

            const data = await resposta.json()

            if (!data || data.length === 0) {
                select_etec.innerHTML = '<option value="" selected disabled>Sem ETECs nesta cidade</option>'
                return
            }

            select_etec.innerHTML = '<option value="" selected disabled>Selecione sua ETEC</option>'
            data.forEach(etec => {
                const opcao = document.createElement('option')
                opcao.value = etec.codigo_etec
                opcao.textContent = `${etec.nome_etec} (${etec.codigo_etec})`
                opcao.dataset.id_etec = etec.id_etec
                select_etec.appendChild(opcao)
            })
        }
        catch (err) {
            console.error(err)
            select_etec.innerHTML = '<option value="" selected disabled>Erro ao carregar ETECs</option>'
        }
    }

    if (select_cidade) {
        select_cidade.addEventListener('change', function () {
            const id_cidade = select_cidade.value
            if (id_cidade) etecs_por_cidade(id_cidade)
        })
    }

    if (button_etec) {
        button_etec.addEventListener('click', function() {
            const etec_escolhida = select_etec.value

            if (!etec_escolhida) {
                select_etec.focus()
                return
            }

            input_etec.value = etec_escolhida

            const modal = instanciar_modal()
            modal.hide()
        })
    }

    if (div_modal_etec) {
        div_modal_etec.addEventListener('show.bs.modal', function () {
            select_etec.innerHTML = '<option value="" selected disabled>Selecione sua ETEC</option>'
            select_cidade.selectedIndex = 0
        })
    }
})
