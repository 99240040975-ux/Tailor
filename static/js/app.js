/* =========================================================
   TailorConnect - Global Application JavaScript
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    initPageLoader();
    initMobileNavigation();
    initFlashMessages();
    initPasswordToggles();
    initFormLoading();
    initScrollReveal();
    initSmoothLinks();
    initRippleEffects();
});


/* =========================================================
   PAGE LOADER
   ========================================================= */

function initPageLoader() {
    const loader = document.querySelector(".page-loader");

    if (!loader) return;

    window.addEventListener("load", () => {
        setTimeout(() => {
            loader.classList.add("hidden");

            setTimeout(() => {
                loader.remove();
            }, 500);
        }, 250);
    });
}


/* =========================================================
   MOBILE NAVIGATION
   ========================================================= */

function initMobileNavigation() {
    const menuButton = document.querySelector(".mobile-menu-button");
    const mobileNav = document.querySelector(".mobile-nav");
    const overlay = document.querySelector(".mobile-nav-overlay");

    if (!menuButton || !mobileNav) return;

    const closeMenu = () => {
        mobileNav.classList.remove("active");
        menuButton.classList.remove("active");

        if (overlay) {
            overlay.classList.remove("active");
        }

        document.body.classList.remove("menu-open");
    };

    const openMenu = () => {
        mobileNav.classList.add("active");
        menuButton.classList.add("active");

        if (overlay) {
            overlay.classList.add("active");
        }

        document.body.classList.add("menu-open");
    };

    menuButton.addEventListener("click", (event) => {
        event.preventDefault();

        if (mobileNav.classList.contains("active")) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    if (overlay) {
        overlay.addEventListener("click", closeMenu);
    }

    mobileNav.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 900) {
            closeMenu();
        }
    });
}


/* =========================================================
   FLASH MESSAGES
   ========================================================= */

function initFlashMessages() {
    const flashMessages = document.querySelectorAll(
        ".flash-message, .alert, .flash"
    );

    flashMessages.forEach((message) => {
        const closeButton = message.querySelector(
            ".flash-close, .alert-close, [data-dismiss]"
        );

        if (closeButton) {
            closeButton.addEventListener("click", () => {
                hideFlash(message);
            });
        }

        // Automatically hide success/info messages.
        if (
            message.classList.contains("success") ||
            message.classList.contains("flash-success") ||
            message.classList.contains("alert-success") ||
            message.classList.contains("info") ||
            message.classList.contains("flash-info")
        ) {
            setTimeout(() => {
                hideFlash(message);
            }, 6000);
        }
    });
}

function hideFlash(element) {
    element.style.opacity = "0";
    element.style.transform = "translateY(-8px)";

    setTimeout(() => {
        element.remove();
    }, 300);
}


/* =========================================================
   PASSWORD TOGGLES
   ========================================================= */

function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll(
        "[data-password-toggle], .password-toggle"
    );

    toggleButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();

            let input = null;

            const targetId = button.getAttribute("data-password-toggle");

            if (targetId) {
                input = document.getElementById(targetId);
            }

            if (!input) {
                const wrapper = button.closest(
                    ".input-shell, .password-field, .form-group"
                );

                if (wrapper) {
                    input = wrapper.querySelector(
                        'input[type="password"], input[type="text"]'
                    );
                }
            }

            if (!input) return;

            if (input.type === "password") {
                input.type = "text";
                button.classList.add("visible");

                const icon = button.querySelector("i");

                if (icon) {
                    icon.classList.remove("fa-eye");
                    icon.classList.add("fa-eye-slash");
                }
            } else {
                input.type = "password";
                button.classList.remove("visible");

                const icon = button.querySelector("i");

                if (icon) {
                    icon.classList.remove("fa-eye-slash");
                    icon.classList.add("fa-eye");
                }
            }
        });
    });
}


/* =========================================================
   FORM LOADING STATE
   ========================================================= */

function initFormLoading() {
    const forms = document.querySelectorAll("form");

    forms.forEach((form) => {
        form.addEventListener("submit", () => {
            if (form.dataset.noLoading === "true") {
                return;
            }

            const submitButton = form.querySelector(
                'button[type="submit"], input[type="submit"]'
            );

            if (!submitButton) return;

            if (submitButton.dataset.loading === "true") {
                return;
            }

            submitButton.dataset.loading = "true";
            submitButton.classList.add("loading");

            if (submitButton.tagName.toLowerCase() === "button") {
                submitButton.dataset.originalText =
                    submitButton.innerHTML;

                submitButton.innerHTML = `
                    <span class="button-spinner"></span>
                    <span>Processing...</span>
                `;

                submitButton.disabled = true;
            } else {
                submitButton.dataset.originalText = submitButton.value;
                submitButton.value = "Processing...";
                submitButton.disabled = true;
            }
        });
    });
}


/* =========================================================
   SCROLL REVEAL
   ========================================================= */

function initScrollReveal() {
    const revealElements = document.querySelectorAll(
        ".reveal, .scroll-reveal, [data-reveal]"
    );

    if (!revealElements.length) return;

    if (!("IntersectionObserver" in window)) {
        revealElements.forEach((element) => {
            element.classList.add("revealed");
        });

        return;
    }

    const observer = new IntersectionObserver(
        (entries, observerInstance) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;

                entry.target.classList.add("revealed");
                observerInstance.unobserve(entry.target);
            });
        },
        {
            threshold: 0.12,
            rootMargin: "0px 0px -40px 0px"
        }
    );

    revealElements.forEach((element) => {
        observer.observe(element);
    });
}


/* =========================================================
   SMOOTH INTERNAL LINKS
   ========================================================= */

function initSmoothLinks() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach((link) => {
        link.addEventListener("click", (event) => {
            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") {
                return;
            }

            const target = document.querySelector(targetId);

            if (!target) return;

            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        });
    });
}


/* =========================================================
   RIPPLE EFFECT
   ========================================================= */

function initRippleEffects() {
    const buttons = document.querySelectorAll(
        ".btn, .button, .cta-button, .nav-button, [data-ripple]"
    );

    buttons.forEach((button) => {
        button.addEventListener("click", function (event) {
            const rect = this.getBoundingClientRect();

            const ripple = document.createElement("span");

            const size = Math.max(rect.width, rect.height);

            ripple.style.width = `${size}px`;
            ripple.style.height = `${size}px`;

            ripple.style.left =
                `${event.clientX - rect.left - size / 2}px`;

            ripple.style.top =
                `${event.clientY - rect.top - size / 2}px`;

            ripple.classList.add("ripple-effect");

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 650);
        });
    });
}


/* =========================================================
   GLOBAL UTILITIES
   ========================================================= */

window.TailorConnect = {

    showLoader() {
        const loader = document.querySelector(".page-loader");

        if (loader) {
            loader.classList.remove("hidden");
        }
    },

    hideLoader() {
        const loader = document.querySelector(".page-loader");

        if (loader) {
            loader.classList.add("hidden");
        }
    },

    showToast(message, type = "info") {
        let container = document.querySelector(".toast-container");

        if (!container) {
            container = document.createElement("div");
            container.className = "toast-container";

            document.body.appendChild(container);
        }

        const toast = document.createElement("div");

        toast.className = `toast toast-${type}`;

        toast.innerHTML = `
            <span class="toast-message"></span>
            <button type="button" class="toast-close" aria-label="Close">
                ×
            </button>
        `;

        toast.querySelector(".toast-message").textContent = message;

        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.add("show");
        });

        toast
            .querySelector(".toast-close")
            .addEventListener("click", () => {
                removeToast(toast);
            });

        setTimeout(() => {
            removeToast(toast);
        }, 4500);
    },

    debounce(callback, delay = 300) {
        let timeout;

        return (...args) => {
            clearTimeout(timeout);

            timeout = setTimeout(() => {
                callback(...args);
            }, delay);
        };
    },

    formatDate(dateValue) {
        if (!dateValue) return "";

        const date = new Date(dateValue);

        if (Number.isNaN(date.getTime())) {
            return dateValue;
        }

        return date.toLocaleDateString("en-IN", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });
    },

    formatCurrency(value) {
        const number = Number(value);

        if (Number.isNaN(number)) {
            return "₹0";
        }

        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }).format(number);
    }
};


/* =========================================================
   TOAST HELPERS
   ========================================================= */

function removeToast(toast) {
    if (!toast) return;

    toast.classList.remove("show");

    setTimeout(() => {
        toast.remove();
    }, 300);
}


/* =========================================================
   DYNAMIC STYLE HELPERS
   ========================================================= */

(function addGlobalDynamicStyles() {
    if (document.getElementById("tailorconnect-js-styles")) {
        return;
    }

    const style = document.createElement("style");

    style.id = "tailorconnect-js-styles";

    style.textContent = `
        body.menu-open {
            overflow: hidden;
        }

        .button-spinner {
            width: 16px;
            height: 16px;
            border: 2px solid currentColor;
            border-right-color: transparent;
            border-radius: 50%;
            display: inline-block;
            animation: tc-spin 0.7s linear infinite;
        }

        @keyframes tc-spin {
            to {
                transform: rotate(360deg);
            }
        }

        .ripple-effect {
            position: absolute;
            border-radius: 50%;
            transform: scale(0);
            animation: tc-ripple 0.65s ease-out;
            background: rgba(255, 255, 255, 0.25);
            pointer-events: none;
        }

        @keyframes tc-ripple {
            to {
                transform: scale(2.5);
                opacity: 0;
            }
        }

        .btn,
        .button,
        .cta-button,
        .nav-button,
        [data-ripple] {
            position: relative;
            overflow: hidden;
        }

        .reveal,
        .scroll-reveal,
        [data-reveal] {
            opacity: 0;
            transform: translateY(24px);
            transition:
                opacity 0.7s ease,
                transform 0.7s ease;
        }

        .reveal.revealed,
        .scroll-reveal.revealed,
        [data-reveal].revealed {
            opacity: 1;
            transform: translateY(0);
        }

        .toast-container {
            position: fixed;
            top: 24px;
            right: 24px;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: min(380px, calc(100vw - 32px));
        }

        .toast {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 14px;
            background: rgba(25, 18, 35, 0.94);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(18px);
            transform: translateX(30px);
            opacity: 0;
            transition:
                opacity 0.3s ease,
                transform 0.3s ease;
        }

        .toast.show {
            opacity: 1;
            transform: translateX(0);
        }

        .toast-message {
            flex: 1;
            font-size: 14px;
            line-height: 1.5;
        }

        .toast-close {
            border: 0;
            background: transparent;
            color: rgba(255, 255, 255, 0.7);
            font-size: 20px;
            cursor: pointer;
            line-height: 1;
        }

        .toast-close:hover {
            color: white;
        }

        @media (max-width: 640px) {
            .toast-container {
                top: 14px;
                right: 14px;
                left: 14px;
                max-width: none;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .reveal,
            .scroll-reveal,
            [data-reveal] {
                opacity: 1;
                transform: none;
                transition: none;
            }

            .ripple-effect {
                animation: none;
            }
        }
    `;

    document.head.appendChild(style);
})();