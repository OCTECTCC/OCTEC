document.addEventListener('DOMContentLoaded', function () {
    const tipo_usuario = document.getElementById('select_usuario');
    let tipo_usuario_anterior = tipo_usuario.value
    const login_label = document.querySelector('label[for="input_login"]');
    const login_input = document.getElementById('input_login');

    function update_login() {
        const opcao = tipo_usuario.options[tipo_usuario.selectedIndex];
        const texto = opcao ? opcao.text : '';

        if (tipo_usuario.value !== tipo_usuario_anterior) {
            login_input.value = ""
        }
        tipo_usuario_anterior = tipo_usuario.value

        if (texto.includes('Aluno')) {
            login_label.textContent = 'RM';
            login_input.placeholder = 'Digite seu RM';
            login_input.minLength = "5";
            login_input.maxLength = "6";
            login_input.pattern = "\\d{5,}";
        }
        else {
            login_label.textContent = 'Login';
            login_input.placeholder = 'Digite seu login';
            login_input.removeAttribute("minLength")
            login_input.removeAttribute("maxLength")
            login_input.removeAttribute("pattern")
        }
    }

    tipo_usuario.addEventListener('change', update_login);

    update_login();
});