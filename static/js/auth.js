/* =========================================================
   TailorConnect - Authentication JavaScript
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    initAuthForms();
    initPasswordStrength();
    initPasswordToggles();
    initAuthTransitions();
});


/* =========================================================
   AUTH FORMS
   ========================================================= */

function initAuthForms() {
    const forms = document.querySelectorAll(
        ".auth-form, #loginForm, #registerForm"
    );

    forms.forEach((form) => {
        form.addEventListener("submit", () => {
            const button = form.querySelector(
                'button[type="submit"]'
            );

            if (!button) return;

            button.classList.add("loading");
            button.disabled = true;

            const original =
                button.dataset.originalText ||
                button.innerHTML;

            button.dataset.originalText =
                original;

            button.innerHTML = `
                <span class="button-spinner"></span>
                <span>Please wait...</span>
            `;
        });
    });
}


/* =========================================================
   PASSWORD STRENGTH
   ========================================================= */

function initPasswordStrength() {
    const passwordInputs = document.querySelectorAll(
        'input[name="password"], #password'
    );

    passwordInputs.forEach((input) => {
        const strengthContainer =
            document.querySelector(
                "[data-password-strength]"
            );

        if (!strengthContainer) return;

        input.addEventListener("input", () => {
            const result =
                calculatePasswordStrength(
                    input.value
                );

            updatePasswordStrength(
                strengthContainer,
                result
            );
        });
    });
}

function calculatePasswordStrength(password) {
    if (!password) {
        return {
            score: 0,
            label: "",
            className: ""
        };
    }

    let score = 0;

    if (password.length >= 8) {
        score++;
    }

    if (/[a-z]/.test(password)) {
        score++;
    }

    if (/[A-Z]/.test(password)) {
        score++;
    }

    if (/[0-9]/.test(password)) {
        score++;
    }

    if (/[^A-Za-z0-9]/.test(password)) {
        score++;
    }

    if (score <= 2) {
        return {
            score,
            label: "Needs improvement",
            className: "weak"
        };
    }

    if (score <= 3) {
        return {
            score,
            label: "Good",
            className: "medium"
        };
    }

    return {
        score,
        label: "Strong",
        className: "strong"
    };
}

function updatePasswordStrength(
    container,
    result
) {
    container.className =
        `password-strength ${result.className}`;

    container.innerHTML = `
        <div class="password-strength-bar">
            ${[1, 2, 3, 4, 5]
                .map(
                    (index) =>
                        `<span class="${
                            index <= result.score
                                ? "filled"
                                : ""
                        }"></span>`
                )
                .join("")}
        </div>

        <span class="password-strength-label">
            ${result.label}
        </span>
    `;
}


/* =========================================================
   PASSWORD VISIBILITY
   ========================================================= */

function initPasswordToggles() {
    const buttons = document.querySelectorAll(
        "[data-password-toggle]"
    );

    buttons.forEach((button) => {
        button.addEventListener(
            "click",
            (event) => {
                event.preventDefault();

                const targetId =
                    button.dataset.passwordToggle;

                const input =
                    document.getElementById(
                        targetId
                    );

                if (!input) return;

                const isPassword =
                    input.type === "password";

                input.type = isPassword
                    ? "text"
                    : "password";

                button.classList.toggle(
                    "visible",
                    isPassword
                );

                const icon =
                    button.querySelector("i");

                if (icon) {
                    icon.classList.toggle(
                        "fa-eye",
                        !isPassword
                    );

                    icon.classList.toggle(
                        "fa-eye-slash",
                        isPassword
                    );
                }
            }
        );
    });
}


/* =========================================================
   AUTH PAGE TRANSITIONS
   ========================================================= */

function initAuthTransitions() {
    const transitionLinks =
        document.querySelectorAll(
            "[data-auth-transition]"
        );

    transitionLinks.forEach((link) => {
        link.addEventListener(
            "click",
            (event) => {
                const href =
                    link.getAttribute("href");

                if (
                    !href ||
                    href === "#" ||
                    href.startsWith("javascript:")
                ) {
                    return;
                }

                event.preventDefault();

                document.body.classList.add(
                    "auth-page-exit"
                );

                setTimeout(() => {
                    window.location.href =
                        href;
                }, 280);
            }
        );
    });
}


/* =========================================================
   EMAIL VALIDATION
   ========================================================= */

window.TailorConnectAuth = {

    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
            String(email || "").trim()
        );
    },

    validateEmailInput(input) {
        if (!input) return false;

        const valid =
            this.isValidEmail(input.value);

        input.classList.toggle(
            "input-error",
            !valid && input.value.length > 0
        );

        return valid;
    },

    validatePassword(password) {
        return String(password || "").length >= 8;
    }
};


/* =========================================================
   AUTH STYLES
   ========================================================= */

(function addAuthStyles() {
    if (
        document.getElementById(
            "tailorconnect-auth-js-styles"
        )
    ) {
        return;
    }

    const style =
        document.createElement("style");

    style.id =
        "tailorconnect-auth-js-styles";

    style.textContent = `
        .button-spinner {
            width: 16px;
            height: 16px;
            display: inline-block;
            border: 2px solid currentColor;
            border-right-color: transparent;
            border-radius: 50%;
            animation:
                auth-spin .7s linear infinite;
        }

        @keyframes auth-spin {
            to {
                transform: rotate(360deg);
            }
        }

        .auth-page-exit {
            opacity: 0;
            transform: scale(.99);
            transition:
                opacity .28s ease,
                transform .28s ease;
        }

        .password-strength {
            margin-top: 8px;
        }

        .password-strength-bar {
            display: flex;
            gap: 4px;
        }

        .password-strength-bar span {
            height: 4px;
            flex: 1;
            border-radius: 999px;
            background: #e8dfe9;
            transition:
                background .2s ease;
        }

        .password-strength-bar span.filled {
            background: #c026d3;
        }

        .password-strength.strong
            .password-strength-bar span.filled {
            background: #16a34a;
        }

        .password-strength.medium
            .password-strength-bar span.filled {
            background: #f59e0b;
        }

        .password-strength.weak
            .password-strength-bar span.filled {
            background: #ef4444;
        }

        .password-strength-label {
            display: block;
            margin-top: 5px;
            color: #8b7c8e;
            font-size: 11px;
        }

        .input-error {
            border-color: #ef4444 !important;
            box-shadow:
                0 0 0 3px
                rgba(239, 68, 68, .1) !important;
        }

        @media (prefers-reduced-motion: reduce) {
            .auth-page-exit {
                transition: none;
            }
        }
    `;

    document.head.appendChild(style);
})();