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

    function update_login() {
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
        tipo_usuario.addEventListener('change', update_login)
    }

    update_login()
})