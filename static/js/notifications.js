// In-App Notifications & Flash message helpers
function showToast(message, type = 'info') {
    const alertsContainer = document.querySelector('.alerts-container');
    if (!alertsContainer) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button type="button" class="close-btn">&times;</button>
    `;
    alertsContainer.appendChild(alert);

    const closeBtn = alert.querySelector('.close-btn');
    closeBtn.addEventListener('click', () => alert.remove());

    setTimeout(() => {
        alert.style.transition = 'opacity 0.5s ease';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
    }, 4000);
}
