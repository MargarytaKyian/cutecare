document.addEventListener('DOMContentLoaded', function() {
    // Керування головним мобільним меню
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const openIcon = document.getElementById('open-icon');
    const closeIcon = document.getElementById('close-icon');

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
            // Перемикання іконок
            if (openIcon && closeIcon) {
                openIcon.classList.toggle('hidden');
                closeIcon.classList.toggle('hidden'); 
            }
        });
    }

    try {
        const observer = new IntersectionObserver((entries, observerInstance) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                    observerInstance.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.2
        });

        const elementsToAnimate = document.querySelectorAll('.animate-on-scroll');
        elementsToAnimate.forEach(el => observer.observe(el));
    } catch (e) {
        console.error("Error initializing IntersectionObserver: ", e);
    }
});