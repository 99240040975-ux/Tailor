// Auth Page Logic: Customer vs Tailor Switcher
document.addEventListener('DOMContentLoaded', function() {
    const roleTabs = document.querySelectorAll('.role-tab');
    const roleInput = document.getElementById('roleInput');
    const tailorFields = document.querySelector('.tailor-only-fields');

    if (roleTabs.length && roleInput) {
        roleTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                roleTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');

                const selectedRole = this.dataset.role;
                roleInput.value = selectedRole;

                if (tailorFields) {
                    if (selectedRole === 'tailor') {
                        tailorFields.classList.add('visible');
                    } else {
                        tailorFields.classList.remove('visible');
                    }
                }
            });
        });
    }

    // Password confirmation match check
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirm_password').value;

            if (password !== confirm) {
                e.preventDefault();
                alert('Passwords do not match! Please check and try again.');
            }
        });
    }
});
