/* ========================================
   Trevieta Header JavaScript
   Mobile Menu Toggle Functionality
   ======================================== */

(function() {
    'use strict';

    function initTrevietaHeader() {
        const mobileToggle = document.querySelector('.trevieta-mobile-toggle');
        const mobileNav = document.querySelector('.trevieta-mobile-nav');
        
        if (!mobileToggle || !mobileNav) return;

        mobileToggle.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Toggle aria-expanded
            this.setAttribute('aria-expanded', !isExpanded);
            
            // Toggle mobile nav
            mobileNav.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            if (!isExpanded) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        // Close mobile menu when clicking on a link
        const mobileNavLinks = mobileNav.querySelectorAll('.trevieta-mobile-nav-link');
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileToggle.setAttribute('aria-expanded', 'false');
                mobileNav.classList.remove('active');
                document.body.style.overflow = '';
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (mobileNav.classList.contains('active') && 
                !mobileNav.contains(e.target) && 
                !mobileToggle.contains(e.target)) {
                mobileToggle.setAttribute('aria-expanded', 'false');
                mobileNav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Close mobile menu on window resize (if window becomes large)
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (window.innerWidth > 991) {
                    mobileToggle.setAttribute('aria-expanded', 'false');
                    mobileNav.classList.remove('active');
                    document.body.style.overflow = '';
                }
            }, 250);
        });
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTrevietaHeader);
    } else {
        initTrevietaHeader();
    }

})();

