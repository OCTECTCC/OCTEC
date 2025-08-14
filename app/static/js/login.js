document.addEventListener('DOMContentLoaded', function () {
    const tipo_usuario = document.getElementById('tipo_usuario');
    const login_label = document.querySelector('label[for="login"]');
    const login_input = document.getElementById('login');

    function update_login() {
        const opcao = tipo_usuario.options[tipo_usuario.selectedIndex];
        const texto = opcao ? opcao.text : '';

        if (texto.includes('Aluno')) {
            login_label.textContent = 'RM';
            login_input.placeholder = 'Digite seu RM';
        }
        else {
            login_label.textContent = 'Login';
            login_input.placeholder = 'Digite seu login';
        }
    }

    tipo_usuario.addEventListener('change', update_login);

    update_login();
});