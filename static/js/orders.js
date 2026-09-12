/* =========================================================
   TailorConnect - Orders JavaScript
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    initOrderFilters();
    initOrderActions();
    initQuotationForms();
    initOrderTimeline();
    initOrderModals();
});


/* =========================================================
   ORDER FILTERS
   ========================================================= */

function initOrderFilters() {
    const filters = document.querySelectorAll(
        "[data-order-filter]"
    );

    filters.forEach((filter) => {
        filter.addEventListener("change", () => {
            filterOrders(
                filter.value,
                filter.dataset.orderTarget || ".order-card"
            );
        });
    });
}

function filterOrders(status, selector) {
    document.querySelectorAll(selector).forEach((order) => {
        const orderStatus = (
            order.dataset.status ||
            order.querySelector(".status-badge")?.textContent ||
            ""
        ).trim().toLowerCase();

        const selected = String(status || "")
            .trim()
            .toLowerCase();

        order.style.display =
            !selected ||
            selected === "all" ||
            orderStatus.includes(selected)
                ? ""
                : "none";
    });
}


/* =========================================================
   ORDER ACTIONS
   ========================================================= */

function initOrderActions() {
    document.addEventListener("click", async (event) => {
        const action = event.target.closest(
            "[data-order-action]"
        );

        if (!action) return;

        const orderId = action.dataset.orderId;
        const actionType = action.dataset.orderAction;

        if (!orderId || !actionType) return;

        if (
            action.dataset.confirm &&
            !window.confirm(action.dataset.confirm)
        ) {
            return;
        }

        if (action.dataset.processing === "true") {
            return;
        }

        action.dataset.processing = "true";
        action.disabled = true;

        try {
            await performOrderAction(
                orderId,
                actionType,
                action
            );
        } finally {
            action.dataset.processing = "false";
            action.disabled = false;
        }
    });
}


/* =========================================================
   PERFORM ORDER ACTION
   ========================================================= */

async function performOrderAction(
    orderId,
    actionType,
    button
) {
    const endpoints = {
        accept: `/orders/${orderId}/accept`,
        confirm: `/orders/${orderId}/confirm`,
        cancel: `/orders/${orderId}/cancel`,
        deliver: `/orders/${orderId}/deliver`
    };

    const endpoint =
        endpoints[actionType] ||
        `/orders/${orderId}/${actionType}`;

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(
                `Order action failed: ${response.status}`
            );
        }

        let data = {};

        try {
            data = await response.json();
        } catch {
            data = {};
        }

        if (data.success === false) {
            throw new Error(
                data.message || "Unable to update order."
            );
        }

        updateOrderAfterAction(
            orderId,
            data
        );

        TailorConnect.showToast(
            data.message ||
            "Order updated successfully.",
            "success"
        );

    } catch (error) {
        console.error(error);

        TailorConnect.showToast(
            error.message ||
            "Unable to update the order.",
            "error"
        );
    }
}


/* =========================================================
   QUOTATION FORMS
   ========================================================= */

function initQuotationForms() {
    const forms = document.querySelectorAll(
        "[data-quotation-form], #quotationForm"
    );

    forms.forEach((form) => {
        form.addEventListener("submit", async (event) => {
            if (
                form.dataset.nativeSubmit === "true"
            ) {
                return;
            }

            event.preventDefault();

            const quotationField =
                form.querySelector(
                    '[name="quotation"], [name="price"]'
                );

            if (
                quotationField &&
                (!quotationField.value ||
                    Number(quotationField.value) < 0)
            ) {
                quotationField.classList.add(
                    "input-error"
                );

                TailorConnect.showToast(
                    "Please enter a valid quotation amount.",
                    "error"
                );

                return;
            }

            const submitButton =
                form.querySelector(
                    'button[type="submit"]'
                );

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.classList.add("loading");
            }

            try {
                const response = await fetch(
                    form.action,
                    {
                        method: "POST",
                        body: new FormData(form),
                        headers: {
                            Accept:
                                "application/json"
                        }
                    }
                );

                if (!response.ok) {
                    throw new Error(
                        "Unable to submit quotation."
                    );
                }

                let data = {};

                try {
                    data =
                        await response.json();
                } catch {
                    data = {};
                }

                if (data.success === false) {
                    throw new Error(
                        data.message ||
                        "Quotation submission failed."
                    );
                }

                TailorConnect.showToast(
                    data.message ||
                    "Quotation submitted successfully.",
                    "success"
                );

                setTimeout(() => {
                    if (data.redirect_url) {
                        window.location.href =
                            data.redirect_url;
                    } else {
                        window.location.reload();
                    }
                }, 700);

            } catch (error) {
                TailorConnect.showToast(
                    error.message ||
                    "Unable to submit quotation.",
                    "error"
                );

                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.classList.remove(
                        "loading"
                    );
                }
            }
        });
    });
}


/* =========================================================
   ORDER TIMELINE
   ========================================================= */

function initOrderTimeline() {
    document
        .querySelectorAll("[data-order-timeline]")
        .forEach((timeline) => {
            const currentStatus =
                timeline.dataset.currentStatus;

            if (!currentStatus) return;

            const statuses = [
                "pending",
                "quoted",
                "confirmed",
                "cutting",
                "stitching",
                "alteration",
                "quality_check",
                "ready",
                "delivered"
            ];

            const currentIndex =
                statuses.indexOf(
                    currentStatus.toLowerCase()
                );

            timeline
                .querySelectorAll(
                    "[data-timeline-status]"
                )
                .forEach((item) => {
                    const status =
                        item.dataset.timelineStatus;

                    const index =
                        statuses.indexOf(
                            status
                                ?.toLowerCase()
                        );

                    item.classList.remove(
                        "active",
                        "completed"
                    );

                    if (index < currentIndex) {
                        item.classList.add(
                            "completed"
                        );
                    } else if (
                        index === currentIndex
                    ) {
                        item.classList.add(
                            "active"
                        );
                    }
                });
        });
}


/* =========================================================
   ORDER MODALS
   ========================================================= */

function initOrderModals() {
    document.addEventListener("click", (event) => {
        const openButton =
            event.target.closest(
                "[data-open-order-modal]"
            );

        if (openButton) {
            event.preventDefault();

            const modalId =
                openButton.dataset.openOrderModal;

            const modal =
                document.getElementById(modalId);

            if (modal) {
                modal.classList.add("active");
                document.body.classList.add(
                    "modal-open"
                );
            }

            return;
        }

        const closeButton =
            event.target.closest(
                "[data-close-order-modal]"
            );

        if (closeButton) {
            event.preventDefault();
            closeAllOrderModals();
        }

        if (
            event.target.classList.contains(
                "modal"
            )
        ) {
            closeAllOrderModals();
        }
    });

    document.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Escape") {
                closeAllOrderModals();
            }
        }
    );
}

function closeAllOrderModals() {
    document
        .querySelectorAll(".modal.active")
        .forEach((modal) => {
            modal.classList.remove("active");
        });

    document.body.classList.remove(
        "modal-open"
    );
}


/* =========================================================
   UPDATE ORDER UI
   ========================================================= */

function updateOrderAfterAction(
    orderId,
    data
) {
    const order =
        document.querySelector(
            `[data-order-id="${orderId}"]`
        );

    if (!order) {
        window.location.reload();
        return;
    }

    const newStatus =
        data.status ||
        data.new_status;

    if (newStatus) {
        order.dataset.status =
            newStatus;

        const badge =
            order.querySelector(
                ".status-badge"
            );

        if (badge) {
            badge.textContent =
                formatStatus(newStatus);

            badge.className =
                `status-badge status-${newStatus
                    .toLowerCase()
                    .replace(/\s+/g, "_")}`;
        }
    }
}


/* =========================================================
   STATUS FORMATTER
   ========================================================= */

function formatStatus(status) {
    return String(status || "")
        .replace(/_/g, " ")
        .replace(/\b\w/g, (letter) =>
            letter.toUpperCase()
        );
}


/* =========================================================
   GLOBAL ORDER API
   ========================================================= */

window.TailorConnectOrders = {

    filter(status) {
        filterOrders(
            status,
            ".order-card"
        );
    },

    closeModals() {
        closeAllOrderModals();
    },

    refresh() {
        window.location.reload();
    }
};


/* =========================================================
   ORDER STYLES
   ========================================================= */

(function addOrderStyles() {
    if (
        document.getElementById(
            "tailorconnect-order-js-styles"
        )
    ) {
        return;
    }

    const style =
        document.createElement("style");

    style.id =
        "tailorconnect-order-js-styles";

    style.textContent = `
        body.modal-open {
            overflow: hidden;
        }

        .modal {
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
            transition:
                opacity .2s ease,
                visibility .2s ease;
        }

        .modal.active {
            opacity: 1;
            visibility: visible;
            pointer-events: auto;
        }

        .loading {
            pointer-events: none;
            opacity: .65;
        }

        .input-error {
            border-color: #ef4444 !important;
            box-shadow:
                0 0 0 3px
                rgba(239, 68, 68, .1) !important;
        }
    `;

    document.head.appendChild(style);
})();