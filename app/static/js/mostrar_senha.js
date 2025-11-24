document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('button[data-toggle-password]').forEach(btn => {
    const target = btn.dataset.target

    if (!target) return

    const input = document.querySelector(target)

    if (!input) return

    btn.setAttribute("tabindex", "-1")

    const parent = btn.parentNode;
    const placeholder = document.createComment('pw-btn-placeholder');

    btn.classList.remove('d-none');
    parent.replaceChild(placeholder, btn);

    let mostrar = false;
    let input_hover = false
    let button_hover = false
    let input_focus = false

    function mostrar_botao() {
      if (!mostrar) {
        parent.replaceChild(btn, placeholder);
        mostrar = true;
      }
    }

    function esconder_botao() {
      if (!input_hover && !button_hover && !input_focus && mostrar) {
        parent.replaceChild(placeholder, btn);
        mostrar = false;
      }
    }

    function mostrar_senha() {
      if (input.type === 'password') {
        input.type = 'text';
        btn.querySelector('i')?.classList.replace('bi-eye', 'bi-eye-slash');
        btn.setAttribute('title', 'Ocultar senha');
      } else {
        input.type = 'password';
        btn.querySelector('i')?.classList.replace('bi-eye-slash', 'bi-eye');
        btn.setAttribute('title', 'Mostrar senha');
      }

      try {
        input.focus()
      } catch(error) {}
    }

    btn.addEventListener('focus', () => {
      try {
        btn.blur()
      } catch (error) {}
    });

    btn.addEventListener('keydown', (evento) => {
      if (evento.key === 'Tab') {
        evento.preventDefault();
      }
    });

    input.addEventListener('mouseenter', () => {
      input_hover = true
      mostrar_botao()
    })

    input.addEventListener('mouseleave', () => {
      input_hover = false
      setTimeout(esconder_botao, 50)
    })

    input.addEventListener('focus', () => {
      input_focus = true
      mostrar_botao()
    })

    input.addEventListener('blur', () => {
      input_focus = false
      setTimeout(esconder_botao, 50)
    })

    btn.addEventListener('mouseenter', () => {
      button_hover = true
    })

    btn.addEventListener('mouseleave', () => {
      button_hover = false
      setTimeout(esconder_botao, 50)
    })

    btn.addEventListener('click', (evento) => {
      evento.preventDefault()
      mostrar_senha()
    })

    if (document.activeElement === input) {
      input_focus = true
      mostrar_botao()
    }
  })
})