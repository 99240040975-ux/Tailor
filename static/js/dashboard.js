// Dashboard Interactive Utilities
document.addEventListener('DOMContentLoaded', function() {
    // Animate numbers on stats cards
    const statNumbers = document.querySelectorAll('.stat-info h3');
    statNumbers.forEach(stat => {
        const text = stat.innerText.trim();
        const num = parseFloat(text.replace(/[^0-9.]/g, ''));
        if (!isNaN(num) && num > 0 && !text.includes('.')) {
            let start = 0;
            const duration = 800;
            const stepTime = 20;
            const steps = duration / stepTime;
            const increment = num / steps;

            const timer = setInterval(() => {
                start += increment;
                if (start >= num) {
                    stat.innerText = text;
                    clearInterval(timer);
                } else {
                    stat.innerText = Math.floor(start);
                }
            }, stepTime);
        }
    });
});
