(function(){
    const colorButtons = document.querySelectorAll('.color-choice')
    const hiddenInput = document.getElementById('cor_avatar_input')
    const avatarPreview = document.getElementById('avatar-preview')

    function clearSelection(){
        colorButtons.forEach(btn => {
            btn.classList.remove('border','border-3','border-white','shadow')
        })
    }

    document.addEventListener('DOMContentLoaded', () => {
        const initialFromInput = hiddenInput && hiddenInput.value ? hiddenInput.value : null
        const initialFromData = avatarPreview && avatarPreview.dataset && avatarPreview.dataset.color ? avatarPreview.dataset.color : null
        const initial = initialFromInput || initialFromData || '#6c757d'
        
        avatarPreview.style.backgroundColor = initial

        colorButtons.forEach(btn => {
            if (btn.dataset.color.toLowerCase() === initial.toLowerCase()){
                btn.classList.add('border','border-3','border-white','shadow')
            }
        })
    })

    colorButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const color = btn.dataset.color
            hiddenInput.value = color
            avatarPreview.style.backgroundColor = color
            clearSelection()
            btn.classList.add('border','border-3','border-white','shadow')
        })
    })

    const form = document.getElementById('form-editar-perfil')
    form.addEventListener('submit', (e) => {
        const val = hiddenInput.value || ''
        if (!/^#[0-9A-Fa-f]{6}$/.test(val)) {
            e.preventDefault()
            alert('Selecione uma cor válida antes de salvar')
        }
    })
})()