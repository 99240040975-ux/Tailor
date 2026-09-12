/* =========================================================
   TailorConnect - Notifications
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    initNotifications();
});


function initNotifications() {
    initNotificationToggle();
    initNotificationDismiss();
    initNotificationPolling();
}


/* =========================================================
   NOTIFICATION PANEL
   ========================================================= */

function initNotificationToggle() {
    const buttons = document.querySelectorAll(
        "[data-notification-toggle], .notification-toggle"
    );

    buttons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();

            const targetId =
                button.dataset.notificationTarget;

            const panel = targetId
                ? document.getElementById(targetId)
                : document.querySelector(
                    ".notification-panel"
                );

            if (!panel) return;

            panel.classList.toggle("active");
            button.classList.toggle("active");
        });
    });

    document.addEventListener("click", (event) => {
        if (
            event.target.closest(
                ".notification-panel, .notification-toggle, [data-notification-toggle]"
            )
        ) {
            return;
        }

        document
            .querySelectorAll(".notification-panel.active")
            .forEach((panel) => {
                panel.classList.remove("active");
            });
    });
}


/* =========================================================
   DISMISS NOTIFICATIONS
   ========================================================= */

function initNotificationDismiss() {
    document.addEventListener("click", (event) => {
        const button =
            event.target.closest(
                "[data-dismiss-notification]"
            );

        if (!button) return;

        const notification =
            button.closest(
                ".notification-item, .notification"
            );

        if (!notification) return;

        notification.style.opacity = "0";
        notification.style.transform =
            "translateX(15px)";

        setTimeout(() => {
            notification.remove();
            updateNotificationCount();
        }, 250);
    });
}


/* =========================================================
   NOTIFICATION POLLING
   ========================================================= */

function initNotificationPolling() {
    const container =
        document.querySelector(
            "[data-notifications]"
        );

    if (!container) return;

    const interval =
        Number(
            container.dataset.notificationInterval
        ) || 30000;

    if (interval < 5000) return;

    setInterval(async () => {
        if (document.hidden) return;

        await fetchNotifications();
    }, interval);
}


/* =========================================================
   FETCH NOTIFICATIONS
   ========================================================= */

async function fetchNotifications() {
    try {
        const response = await fetch(
            "/notifications",
            {
                headers: {
                    Accept: "application/json"
                }
            }
        );

        if (!response.ok) return;

        const data = await response.json();

        updateNotificationUI(data);

    } catch (error) {
        console.debug(
            "Notification refresh unavailable:",
            error
        );
    }
}


/* =========================================================
   UPDATE UI
   ========================================================= */

function updateNotificationUI(data) {
    if (!data) return;

    const notifications =
        Array.isArray(data)
            ? data
            : data.notifications || [];

    const count =
        data.unread_count ??
        data.unread ??
        notifications.filter(
            (item) => !item.read
        ).length;

    updateNotificationCount(count);

    const container =
        document.querySelector(
            "[data-notifications]"
        );

    if (!container) return;

    renderNotifications(
        container,
        notifications
    );
}


/* =========================================================
   RENDER NOTIFICATIONS
   ========================================================= */

function renderNotifications(
    container,
    notifications
) {
    if (!notifications.length) {
        container.innerHTML = `
            <div class="notification-empty">
                <div class="notification-empty-icon">✦</div>
                <strong>You're all caught up</strong>
                <span>No new notifications right now.</span>
            </div>
        `;

        return;
    }

    container.innerHTML = notifications
        .map((notification) => {
            const id =
                notification.id ?? "";

            const title =
                escapeHtml(
                    notification.title ||
                    "Notification"
                );

            const message =
                escapeHtml(
                    notification.message ||
                    notification.body ||
                    ""
                );

            const createdAt =
                notification.created_at
                    ? TailorConnect.formatDate(
                        notification.created_at
                    )
                    : "";

            const unread =
                !notification.read;

            return `
                <div
                    class="notification-item ${unread ? "unread" : ""}"
                    data-notification-id="${id}"
                >
                    <div class="notification-icon">
                        ✦
                    </div>

                    <div class="notification-content">
                        <strong>${title}</strong>
                        <p>${message}</p>

                        ${
                            createdAt
                                ? `<small>${createdAt}</small>`
                                : ""
                        }
                    </div>

                    ${
                        unread
                            ? `
                                <button
                                    type="button"
                                    class="notification-read"
                                    data-mark-read="${id}"
                                    aria-label="Mark as read"
                                >
                                    ✓
                                </button>
                            `
                            : ""
                    }
                </div>
            `;
        })
        .join("");

    bindMarkReadButtons();
}


/* =========================================================
   MARK AS READ
   ========================================================= */

function bindMarkReadButtons() {
    document
        .querySelectorAll("[data-mark-read]")
        .forEach((button) => {
            button.addEventListener(
                "click",
                async () => {
                    const id =
                        button.dataset.markRead;

                    if (!id) return;

                    try {
                        const response =
                            await fetch(
                                `/notifications/${encodeURIComponent(id)}/read`,
                                {
                                    method: "POST",
                                    headers: {
                                        Accept:
                                            "application/json"
                                    }
                                }
                            );

                        if (!response.ok) return;

                        const item =
                            button.closest(
                                ".notification-item"
                            );

                        if (item) {
                            item.classList.remove(
                                "unread"
                            );
                        }

                        button.remove();

                        updateNotificationCount();

                    } catch (error) {
                        console.error(
                            "Unable to mark notification as read:",
                            error
                        );
                    }
                }
            );
        });
}


/* =========================================================
   COUNT
   ========================================================= */

function updateNotificationCount(
    explicitCount = null
) {
    let count = explicitCount;

    if (count === null) {
        count = document.querySelectorAll(
            ".notification-item.unread"
        ).length;
    }

    const badges = document.querySelectorAll(
        ".notification-count, [data-notification-count]"
    );

    badges.forEach((badge) => {
        badge.textContent = count;

        if (Number(count) > 0) {
            badge.classList.add("visible");
        } else {
            badge.classList.remove("visible");
        }
    });
}


/* =========================================================
   ESCAPE HTML
   ========================================================= */

function escapeHtml(value) {
    const element =
        document.createElement("div");

    element.textContent =
        String(value ?? "");

    return element.innerHTML;
}


/* =========================================================
   GLOBAL API
   ========================================================= */

window.TailorConnectNotifications = {

    refresh() {
        return fetchNotifications();
    },

    updateCount(count) {
        updateNotificationCount(count);
    }
};


/* =========================================================
   NOTIFICATION STYLES
   ========================================================= */

(function addNotificationStyles() {
    if (
        document.getElementById(
            "tailorconnect-notification-styles"
        )
    ) {
        return;
    }

    const style =
        document.createElement("style");

    style.id =
        "tailorconnect-notification-styles";

    style.textContent = `
        .notification-panel {
            opacity: 0;
            visibility: hidden;
            transform: translateY(-8px);
            transition:
                opacity .2s ease,
                transform .2s ease,
                visibility .2s ease;
        }

        .notification-panel.active {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .notification-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 14px;
            border-bottom: 1px solid #eee5ef;
            transition:
                opacity .25s ease,
                transform .25s ease,
                background .2s ease;
        }

        .notification-item:hover {
            background: #fff8ff;
        }

        .notification-item.unread {
            background: #fdf4ff;
        }

        .notification-icon {
            width: 34px;
            height: 34px;
            flex: 0 0 34px;
            display: grid;
            place-items: center;
            border-radius: 11px;
            color: #a21caf;
            background: #fae8ff;
        }

        .notification-content {
            min-width: 0;
            flex: 1;
        }

        .notification-content strong {
            display: block;
            color: #352239;
            font-size: 13px;
        }

        .notification-content p {
            margin: 4px 0 0;
            color: #817481;
            font-size: 12px;
            line-height: 1.5;
        }

        .notification-content small {
            display: block;
            margin-top: 5px;
            color: #a095a3;
            font-size: 10px;
        }

        .notification-read {
            width: 28px;
            height: 28px;
            border: 0;
            border-radius: 9px;
            color: #16a34a;
            background: #dcfce7;
            cursor: pointer;
        }

        .notification-empty {
            display: flex;
            align-items: center;
            flex-direction: column;
            gap: 5px;
            padding: 35px 20px;
            text-align: center;
        }

        .notification-empty-icon {
            width: 44px;
            height: 44px;
            display: grid;
            place-items: center;
            margin-bottom: 6px;
            border-radius: 14px;
            color: #a21caf;
            background: #fae8ff;
        }

        .notification-empty strong {
            color: #352239;
            font-size: 14px;
        }

        .notification-empty span {
            color: #918491;
            font-size: 12px;
        }

        .notification-count {
            display: none;
        }

        .notification-count.visible {
            display: inline-flex;
        }
    `;

    document.head.appendChild(style);
})();