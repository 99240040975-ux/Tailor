/* =========================================================
   TailorConnect - Dashboard JavaScript
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    initDashboardAnimations();
    initDashboardSearch();
    initStatusFilters();
    initDashboardCounters();
    initConfirmActions();
    initAutoRefresh();
});


/* =========================================================
   DASHBOARD ANIMATIONS
   ========================================================= */

function initDashboardAnimations() {
    const cards = document.querySelectorAll(
        ".stat-card, .dashboard-card, .action-card, .order-card"
    );

    cards.forEach((card, index) => {
        card.style.animationDelay = `${Math.min(index * 60, 400)}ms`;
        card.classList.add("dashboard-enter");
    });
}


/* =========================================================
   DASHBOARD SEARCH
   ========================================================= */

function initDashboardSearch() {
    const searchInputs = document.querySelectorAll(
        "[data-dashboard-search], #dashboardSearch, .dashboard-search input"
    );

    searchInputs.forEach((input) => {
        input.addEventListener(
            "input",
            TailorConnect.debounce(() => {
                const query = input.value.trim().toLowerCase();

                const container =
                    input.closest(".dashboard-card") ||
                    document;

                const items = container.querySelectorAll(
                    "[data-searchable], .order-card, .action-card"
                );

                items.forEach((item) => {
                    const text = item.textContent.toLowerCase();

                    item.style.display =
                        !query || text.includes(query)
                            ? ""
                            : "none";
                });
            }, 180)
        );
    });
}


/* =========================================================
   STATUS FILTERS
   ========================================================= */

function initStatusFilters() {
    const filters = document.querySelectorAll(
        "[data-status-filter]"
    );

    filters.forEach((filter) => {
        filter.addEventListener("change", () => {
            const value = filter.value.toLowerCase();

            const targetSelector =
                filter.dataset.statusTarget ||
                ".order-card";

            const target = document.querySelectorAll(
                targetSelector
            );

            target.forEach((item) => {
                const status =
                    (
                        item.dataset.status ||
                        item.querySelector(".status-badge")?.textContent ||
                        ""
                    )
                        .trim()
                        .toLowerCase();

                item.style.display =
                    !value ||
                    value === "all" ||
                    status.includes(value)
                        ? ""
                        : "none";
            });
        });
    });
}


/* =========================================================
   ANIMATED COUNTERS
   ========================================================= */

function initDashboardCounters() {
    const counters = document.querySelectorAll(
        "[data-counter]"
    );

    if (!counters.length) return;

    if (
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
        counters.forEach((counter) => {
            counter.textContent =
                counter.dataset.counter || counter.textContent;
        });

        return;
    }

    counters.forEach((counter) => {
        const target = Number(counter.dataset.counter);

        if (Number.isNaN(target)) return;

        animateCounter(counter, target);
    });
}

function animateCounter(element, target) {
    const duration = 900;
    const start = performance.now();

    function update(currentTime) {
        const progress = Math.min(
            (currentTime - start) / duration,
            1
        );

        const eased =
            1 - Math.pow(1 - progress, 3);

        const value = Math.round(target * eased);

        element.textContent = value.toLocaleString("en-IN");

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}


/* =========================================================
   CONFIRM ACTIONS
   ========================================================= */

function initConfirmActions() {
    const actions = document.querySelectorAll(
        "[data-confirm]"
    );

    actions.forEach((action) => {
        action.addEventListener("click", (event) => {
            const message =
                action.dataset.confirm ||
                "Are you sure you want to continue?";

            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });
}


/* =========================================================
   OPTIONAL AUTO REFRESH
   ========================================================= */

function initAutoRefresh() {
    const refreshElement = document.querySelector(
        "[data-auto-refresh]"
    );

    if (!refreshElement) return;

    const interval =
        Number(refreshElement.dataset.autoRefresh) || 30000;

    if (interval < 5000) return;

    setInterval(() => {
        if (document.hidden) return;

        const event = new CustomEvent(
            "tailorconnect:refresh"
        );

        document.dispatchEvent(event);
    }, interval);
}


/* =========================================================
   DASHBOARD HELPERS
   ========================================================= */

window.TailorConnectDashboard = {

    refresh() {
        document.dispatchEvent(
            new CustomEvent("tailorconnect:refresh")
        );
    },

    setLoading(element, loading = true) {
        if (!element) return;

        if (loading) {
            element.classList.add("loading");
            element.disabled = true;
        } else {
            element.classList.remove("loading");
            element.disabled = false;
        }
    },

    filterOrders(status) {
        const orders = document.querySelectorAll(
            ".order-card"
        );

        orders.forEach((order) => {
            const orderStatus =
                (
                    order.dataset.status ||
                    order.querySelector(".status-badge")?.textContent ||
                    ""
                )
                    .trim()
                    .toLowerCase();

            order.style.display =
                !status ||
                status === "all" ||
                orderStatus.includes(status.toLowerCase())
                    ? ""
                    : "none";
        });
    }
};


/* =========================================================
   DASHBOARD STYLES
   ========================================================= */

(function addDashboardStyles() {
    if (
        document.getElementById(
            "tailorconnect-dashboard-js-styles"
        )
    ) {
        return;
    }

    const style = document.createElement("style");

    style.id =
        "tailorconnect-dashboard-js-styles";

    style.textContent = `
        .dashboard-enter {
            opacity: 0;
            transform: translateY(14px);
            animation: dashboardEnter .55s ease forwards;
        }

        @keyframes dashboardEnter {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .loading {
            pointer-events: none;
            opacity: .7;
        }

        @media (prefers-reduced-motion: reduce) {
            .dashboard-enter {
                opacity: 1;
                transform: none;
                animation: none;
            }
        }
    `;

    document.head.appendChild(style);
})();