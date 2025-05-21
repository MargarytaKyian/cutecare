document.addEventListener('DOMContentLoaded', function() {
    // Керування головним мобільним меню
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const openIcon = document.getElementById('open-icon');
    const closeIcon = document.getElementById('close-icon');

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
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


    // Вікно детальної інформації (відгуки)
    const reviewTextArea = document.getElementById('review-text-area');
    if (reviewTextArea) {
      reviewTextArea.addEventListener('input', () => {
        reviewTextArea.style.height = 'auto'; 
        reviewTextArea.style.height = reviewTextArea.scrollHeight + 'px'; 
      });
    }

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;

            const targetId = href.substring(1);
            let targetElement = document.getElementById(targetId);

            if (targetId === 'reviews-tab-content' || this.href.includes('#reviews-tab-content')) {
                const reviewsTabButton = document.getElementById('reviews-tab');
                if (reviewsTabButton) {
                    const tabContainer = reviewsTabButton.closest('[x-data]');
                    if (tabContainer && tabContainer.__x) {
                        if (tabContainer.__x.data.activeTab !== undefined) {
                            tabContainer.__x.data.activeTab = 'reviews';
                        } else {
                            reviewsTabButton.click();
                        }
                    } else {
                       reviewsTabButton.click();
                    }
                }
                if (!targetElement) targetElement = document.getElementById('reviews-tab-content');
            }
            
            if (targetElement) {
                e.preventDefault();
                setTimeout(() => {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }, 100);
            }
        });
    });
});