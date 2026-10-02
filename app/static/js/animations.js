// =========================================================
// SetFit Gym - GSAP Animations
// =========================================================

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize GSAP
    gsap.registerPlugin(ScrollTrigger, TextPlugin);
    
    // Check if user prefers reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // If user prefers reduced motion, skip animations
    if (prefersReducedMotion) {
        console.log('Reduced motion preference detected - animations disabled');
        return;
    }
    
    // Initialize animations based on current page
    initPageAnimations();
    initScrollAnimations();
    initInteractiveAnimations();
});

// =========================================================
// PAGE-SPECIFIC ANIMATIONS
// =========================================================

function initPageAnimations() {
    const currentPath = window.location.pathname;
    
    // Homepage animations
    if (currentPath === '/' || currentPath === '/index.html' || currentPath === '') {
        initHomepageAnimations();
    }
    
    // Dashboard animations
    if (currentPath.includes('/dashboard')) {
        initDashboardAnimations();
    }
    
    // Pricing page animations
    if (currentPath.includes('/pricing')) {
        initPricingAnimations();
    }
}

// =========================================================
// HOMEPAGE ANIMATIONS
// =========================================================

function initHomepageAnimations() {
    // Hero section animations
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        // Animate hero badge
        gsap.from('.hero .badge-soft', {
            duration: 0.8,
            y: 20,
            opacity: 0,
            ease: 'power2.out',
            delay: 0.2
        });
        
        // Animate hero title
        gsap.from('.hero h1', {
            duration: 1,
            y: 30,
            opacity: 0,
            ease: 'power3.out',
            delay: 0.4,
            stagger: 0.1
        });
        
        // Animate hero description
        gsap.from('.hero .lead', {
            duration: 0.8,
            y: 20,
            opacity: 0,
            ease: 'power2.out',
            delay: 0.8
        });
        
        // Animate hero buttons
        gsap.from('.hero .btn', {
            duration: 0.6,
            y: 20,
            opacity: 0,
            ease: 'back.out(1.7)',
            delay: 1,
            stagger: 0.1
        });
        
        // Animate hero stats
        gsap.from('.hero .stat-value', {
            duration: 0.8,
            scale: 0.5,
            opacity: 0,
            ease: 'back.out(1.7)',
            delay: 1.2,
            stagger: 0.1
        });
        
        gsap.from('.hero .stat-label', {
            duration: 0.6,
            y: 10,
            opacity: 0,
            ease: 'power2.out',
            delay: 1.4,
            stagger: 0.05
        });
    }
    
    // Features section animations
    const featuresSection = document.querySelector('#features');
    if (featuresSection) {
        // Animate section title
        gsap.from('#features .section-title', {
            scrollTrigger: {
                trigger: '#features',
                start: 'top 80%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.8,
            y: 30,
            opacity: 0,
            ease: 'power3.out'
        });
        
        // Animate section subtitle
        gsap.from('#features .section-subtitle', {
            scrollTrigger: {
                trigger: '#features',
                start: 'top 80%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.8,
            y: 20,
            opacity: 0,
            ease: 'power2.out',
            delay: 0.2
        });
        
        // Animate feature cards with staggered entrance
        gsap.from('#features .card', {
            scrollTrigger: {
                trigger: '#features',
                start: 'top 70%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.6,
            y: 40,
            opacity: 0,
            ease: 'power2.out',
            stagger: 0.1
        });
        
        // Animate activity cards
        gsap.from('.activity-card', {
            scrollTrigger: {
                trigger: '.activity-card',
                start: 'top 80%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.8,
            y: 30,
            opacity: 0,
            ease: 'power2.out',
            stagger: 0.2
        });
    }
    
    // Pricing section animations
    const pricingSection = document.querySelector('#pricing');
    if (pricingSection) {
        // Animate pricing cards with pop effect
        gsap.from('#pricing .plan-card', {
            scrollTrigger: {
                trigger: '#pricing',
                start: 'top 70%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.7,
            scale: 0.8,
            opacity: 0,
            ease: 'back.out(1.7)',
            stagger: 0.15
        });
        
        // Highlight popular plan with subtle pulse
        const popularPlan = document.querySelector('.plan-card.popular');
        if (popularPlan) {
            gsap.to(popularPlan, {
                scrollTrigger: {
                    trigger: popularPlan,
                    start: 'top 80%',
                    toggleActions: 'play none none reverse'
                },
                duration: 1.5,
                boxShadow: '0 20px 40px rgba(255, 107, 53, 0.25)',
                ease: 'power2.inOut',
                yoyo: true,
                repeat: 1
            });
        }
    }
    
    // Enquiry form animations
    const enquirySection = document.querySelector('#enquiry');
    if (enquirySection) {
        gsap.from('#enquiry .card', {
            scrollTrigger: {
                trigger: '#enquiry',
                start: 'top 80%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.8,
            y: 30,
            opacity: 0,
            ease: 'power2.out'
        });
        
        // Animate form elements with slight delay
        gsap.from('#enquiry .form-control, #enquiry .btn', {
            scrollTrigger: {
                trigger: '#enquiry',
                start: 'top 70%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.5,
            y: 20,
            opacity: 0,
            ease: 'power2.out',
            stagger: 0.05,
            delay: 0.2
        });
    }
}

// =========================================================
// DASHBOARD ANIMATIONS
// =========================================================

function initDashboardAnimations() {
    // Welcome message animation
    gsap.from('.section-title', {
        duration: 0.8,
        y: 20,
        opacity: 0,
        ease: 'power2.out'
    });
    
    // Dashboard cards entrance
    gsap.from('.card', {
        duration: 0.6,
        y: 30,
        opacity: 0,
        ease: 'power2.out',
        stagger: 0.1,
        delay: 0.3
    });
    
    // Quick actions buttons
    gsap.from('.d-grid.gap-2 .btn', {
        duration: 0.5,
        x: -20,
        opacity: 0,
        ease: 'power2.out',
        stagger: 0.05,
        delay: 0.5
    });
    
    // Admin/trainer cards
    gsap.from('.row.g-3 .card', {
        duration: 0.6,
        scale: 0.9,
        opacity: 0,
        ease: 'back.out(1.7)',
        stagger: 0.1
    });
}

// =========================================================
// PRICING PAGE ANIMATIONS
// =========================================================

function initPricingAnimations() {
    // Page title animation
    gsap.from('h1.text-center', {
        duration: 0.8,
        y: 30,
        opacity: 0,
        ease: 'power3.out'
    });
    
    // Page subtitle animation
    gsap.from('.text-center.text-muted', {
        duration: 0.6,
        y: 20,
        opacity: 0,
        ease: 'power2.out',
        delay: 0.2
    });
    
    // Pricing cards animation
    gsap.from('.card.h-100', {
        duration: 0.7,
        y: 40,
        opacity: 0,
        ease: 'power2.out',
        stagger: 0.15
    });
}

// =========================================================
// SCROLL-BASED ANIMATIONS
// =========================================================

function initScrollAnimations() {
    // Animate sections on scroll
    gsap.utils.toArray('section').forEach(section => {
        gsap.from(section, {
            scrollTrigger: {
                trigger: section,
                start: 'top 85%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.8,
            y: 30,
            opacity: 0,
            ease: 'power2.out'
        });
    });
    
    // Animate cards on scroll
    gsap.utils.toArray('.card-hover').forEach(card => {
        // Add scroll-triggered entrance
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 85%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.6,
            y: 20,
            opacity: 0,
            ease: 'power2.out'
        });
    });
    
    // Animate feature icons on scroll
    gsap.utils.toArray('.feature-icon').forEach(icon => {
        gsap.from(icon, {
            scrollTrigger: {
                trigger: icon,
                start: 'top 90%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.8,
            scale: 0,
            rotation: 180,
            ease: 'back.out(1.7)'
        });
    });
}

// =========================================================
// INTERACTIVE ANIMATIONS
// =========================================================

function initInteractiveAnimations() {
    // Card hover animations
    const cards = document.querySelectorAll('.card-hover');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            if (window.innerWidth > 768) { // Only on desktop
                gsap.to(card, {
                    duration: 0.3,
                    y: -5,
                    boxShadow: '0 20px 40px rgba(15, 22, 33, 0.15)',
                    ease: 'power2.out'
                });
            }
        });
        
        card.addEventListener('mouseleave', () => {
            if (window.innerWidth > 768) { // Only on desktop
                gsap.to(card, {
                    duration: 0.3,
                    y: 0,
                    boxShadow: 'var(--shadow-sm)',
                    ease: 'power2.out'
                });
            }
        });
    });
    
    // Button hover animations
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            gsap.to(button, {
                duration: 0.2,
                scale: 1.05,
                ease: 'power2.out'
            });
        });
        
        button.addEventListener('mouseleave', () => {
            gsap.to(button, {
                duration: 0.2,
                scale: 1,
                ease: 'power2.out'
            });
        });
    });
    
    // Navbar link hover animations
    const navLinks = document.querySelectorAll('.navbar .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            gsap.to(link, {
                duration: 0.2,
                color: '#ffffff',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                ease: 'power2.out'
            });
        });
        
        link.addEventListener('mouseleave', () => {
            if (!link.classList.contains('active')) {
                gsap.to(link, {
                    duration: 0.2,
                    color: 'rgba(255, 255, 255, 0.75)',
                    backgroundColor: 'transparent',
                    ease: 'power2.out'
                });
            }
        });
    });
    
    // Form focus animations
    const formInputs = document.querySelectorAll('.form-control, .form-select');
    formInputs.forEach(input => {
        input.addEventListener('focus', () => {
            gsap.to(input, {
                duration: 0.2,
                borderColor: 'var(--brand)',
                boxShadow: '0 0 0 3px var(--brand-soft)',
                ease: 'power2.out'
            });
        });
        
        input.addEventListener('blur', () => {
            gsap.to(input, {
                duration: 0.2,
                borderColor: 'var(--border)',
                boxShadow: 'none',
                ease: 'power2.out'
            });
        });
    });
    
    // Flash message animations
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        gsap.from(message, {
            duration: 0.5,
            y: -20,
            opacity: 0,
            ease: 'back.out(1.7)'
        });
        
        // Auto-remove flash messages after 5 seconds
        setTimeout(() => {
            gsap.to(message, {
                duration: 0.3,
                opacity: 0,
                y: -10,
                ease: 'power2.out',
                onComplete: () => {
                    message.style.display = 'none';
                }
            });
        }, 5000);
    });
}

// =========================================================
// UTILITY FUNCTIONS
// =========================================================

// Debounce function for performance
function debounce(func, wait = 20, immediate = true) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Check if element is in viewport
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.8 &&
        rect.bottom >= 0
    );
}

// Reinitialize animations on window resize (with debounce)
window.addEventListener('resize', debounce(() => {
    ScrollTrigger.refresh();
}, 250));

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    ScrollTrigger.getAll().forEach(trigger => trigger.kill());
    gsap.killTweensOf('*');
});

// =========================================================
// PERFORMANCE OPTIMIZATIONS
// =========================================================

// Use requestAnimationFrame for smooth animations
let lastScrollTime = 0;
window.addEventListener('scroll', () => {
    const now = Date.now();
    if (now - lastScrollTime > 100) { // Throttle to 10fps during scroll
        lastScrollTime = now;
        // Update any scroll-based animations here
    }
}, { passive: true });

// Lazy load animations for offscreen elements
const observerOptions = {
    root: null,
    rootMargin: '50px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // Element is in viewport, trigger animation
            gsap.from(entry.target, {
                duration: 0.6,
                y: 20,
                opacity: 0,
                ease: 'power2.out'
            });
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements for lazy animation
document.addEventListener('DOMContentLoaded', () => {
    const lazyAnimateElements = document.querySelectorAll('.card, .feature-icon, .section-title');
    lazyAnimateElements.forEach(el => {
        observer.observe(el);
    });
});

console.log('SetFit Gym animations loaded successfully!');


// =========================================================
// HERO BACKGROUND SLIDER ENHANCEMENT
// =========================================================

function initHeroSlider() {
    const heroSlider = document.querySelector('.hero-slider');
    if (!heroSlider) return;
    
    const slides = heroSlider.querySelectorAll('.hero-slide');
    if (slides.length === 0) return;
    
    // Check if user prefers reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
        // Show only first slide for reduced motion
        slides.forEach((slide, index) => {
            slide.style.opacity = index === 0 ? '1' : '0';
        });
        return;
    }
    
    let currentSlide = 0;
    const slideCount = slides.length;
    const slideDuration = 8000; // 8 seconds per slide
    
    // Enhanced slide transition with GSAP
    function transitionToSlide(index) {
        const prevSlide = currentSlide;
        currentSlide = index;
        
        // Fade out previous slide
        gsap.to(slides[prevSlide], {
            duration: 1.5,
            opacity: 0,
            ease: 'power2.inOut'
        });
        
        // Fade in and zoom current slide
        gsap.fromTo(slides[currentSlide],
            {
                opacity: 0,
                scale: 1
            },
            {
                duration: 1.5,
                opacity: 1,
                scale: 1.1,
                ease: 'power2.inOut'
            }
        );
        
        // Add subtle pan effect
        gsap.to(slides[currentSlide], {
            duration: slideDuration / 1000,
            x: '-5%',
            ease: 'sine.inOut',
            repeat: 1,
            yoyo: true
        });
    }
    
    // Auto-advance slides
    let sliderInterval = setInterval(() => {
        const nextSlide = (currentSlide + 1) % slideCount;
        transitionToSlide(nextSlide);
    }, slideDuration);
    
    // Pause slider on hover (desktop only)
    if (window.innerWidth > 768) {
        heroSlider.addEventListener('mouseenter', () => {
            clearInterval(sliderInterval);
        });
        
        heroSlider.addEventListener('mouseleave', () => {
            sliderInterval = setInterval(() => {
                const nextSlide = (currentSlide + 1) % slideCount;
                transitionToSlide(nextSlide);
            }, slideDuration);
        });
    }
    
    // Add keyboard navigation for accessibility
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            const prevSlide = (currentSlide - 1 + slideCount) % slideCount;
            clearInterval(sliderInterval);
            transitionToSlide(prevSlide);
        } else if (e.key === 'ArrowRight') {
            const nextSlide = (currentSlide + 1) % slideCount;
            clearInterval(sliderInterval);
            transitionToSlide(nextSlide);
        }
    });
    
    // Initialize first slide
    gsap.set(slides[0], { opacity: 1, scale: 1.05 });
    gsap.set(slides.slice(1), { opacity: 0, scale: 1 });
    
    // Add pan animation to first slide
    gsap.to(slides[0], {
        duration: slideDuration / 1000,
        x: '-5%',
        ease: 'sine.inOut',
        repeat: 1,
        yoyo: true
    });
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        clearInterval(sliderInterval);
    });
    
    console.log('Hero slider initialized with', slideCount, 'slides');
}

// Initialize hero slider when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initHeroSlider();
});


// =========================================================
// LANDING PAGE ENHANCEMENTS ANIMATIONS
// =========================================================

// Trust indicators animation
function initTrustIndicators() {
    const trustSection = document.querySelector('.trust-section');
    if (!trustSection) return;
    
    gsap.from('.trust-item', {
        scrollTrigger: {
            trigger: '.trust-section',
            start: 'top 80%',
            toggleActions: 'play none none reverse'
        },
        duration: 0.6,
        y: 30,
        opacity: 0,
        ease: 'back.out(1.7)',
        stagger: 0.1
    });
}

// Testimonials animation
function initTestimonials() {
    const testimonialsSection = document.querySelector('.testimonials-section');
    if (!testimonialsSection) return;
    
    // Animate section title
    gsap.from('.testimonials-section .section-title', {
        scrollTrigger: {
            trigger: '.testimonials-section',
            start: 'top 80%',
            toggleActions: 'play none none reverse'
        },
        duration: 0.8,
        y: 30,
        opacity: 0,
        ease: 'power3.out'
    });
    
    // Animate testimonial cards
    gsap.from('.testimonial-card', {
        scrollTrigger: {
            trigger: '.testimonials-section',
            start: 'top 70%',
            toggleActions: 'play none none reverse'
        },
        duration: 0.7,
        y: 40,
        opacity: 0,
        ease: 'power2.out',
        stagger: 0.15
    });
    
    // Add hover effect for testimonial cards
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    testimonialCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            if (window.innerWidth > 768) {
                gsap.to(card, {
                    duration: 0.3,
                    y: -8,
                    boxShadow: '0 20px 40px rgba(15, 22, 33, 0.15)',
                    ease: 'power2.out'
                });
            }
        });
        
        card.addEventListener('mouseleave', () => {
            if (window.innerWidth > 768) {
                gsap.to(card, {
                    duration: 0.3,
                    y: 0,
                    boxShadow: 'var(--shadow-sm)',
                    ease: 'power2.out'
                });
            }
        });
    });
}

// Initialize new animations on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initTrustIndicators();
    initTestimonials();
});


// =========================================================
// ENHANCED DASHBOARD ANIMATIONS
// =========================================================

function initEnhancedDashboard() {
    const dashboard = document.querySelector('.container.py-5');
    if (!dashboard) return;
    
    // Dashboard header animation
    gsap.from('.dashboard-header', {
        duration: 0.6,
        y: -20,
        opacity: 0,
        ease: 'power2.out'
    });
    
    // Member dashboard animations
    const membershipCard = document.querySelector('.membership-card');
    if (membershipCard) {
        gsap.from('.membership-card', {
            duration: 0.8,
            y: 30,
            opacity: 0,
            ease: 'power2.out',
            delay: 0.2
        });
        
        // Animate stat boxes
        gsap.from('.stat-box', {
            duration: 0.6,
            scale: 0.8,
            opacity: 0,
            ease: 'back.out(1.7)',
            stagger: 0.1,
            delay: 0.5
        });
        
        // Animate progress bar
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            const targetWidth = progressBar.style.width;
            gsap.from(progressBar, {
                duration: 1.5,
                width: '0%',
                ease: 'power2.out',
                delay: 0.8
            });
        }
        
        // Quick actions animation
        gsap.from('.quick-actions-card', {
            duration: 0.8,
            x: 30,
            opacity: 0,
            ease: 'power2.out',
            delay: 0.4
        });
        
        gsap.from('.quick-action-btn', {
            duration: 0.5,
            x: -20,
            opacity: 0,
            ease: 'power2.out',
            stagger: 0.1,
            delay: 0.7
        });
    }
    
    // Admin dashboard animations
    const statCards = document.querySelectorAll('.stat-card-dashboard');
    if (statCards.length > 0) {
        gsap.from(statCards, {
            duration: 0.6,
            y: 30,
            opacity: 0,
            ease: 'back.out(1.7)',
            stagger: 0.1,
            delay: 0.2
        });
        
        // Animate stat values with counter effect
        statCards.forEach((card, index) => {
            const valueElement = card.querySelector('.stat-card-value');
            if (valueElement) {
                const targetValue = valueElement.textContent;
                const numericValue = parseInt(targetValue.replace(/\D/g, ''));
                
                if (!isNaN(numericValue)) {
                    gsap.from(valueElement, {
                        duration: 1.5,
                        textContent: 0,
                        snap: { textContent: 1 },
                        ease: 'power1.inOut',
                        delay: 0.4 + (index * 0.1),
                        onUpdate: function() {
                            const currentValue = Math.round(this.targets()[0].textContent);
                            valueElement.textContent = targetValue.includes('+') 
                                ? currentValue + '+' 
                                : currentValue;
                        }
                    });
                }
            }
        });
    }
    
    // Admin action cards animation
    const adminCards = document.querySelectorAll('.admin-action-card');
    if (adminCards.length > 0) {
        gsap.from(adminCards, {
            duration: 0.7,
            y: 40,
            opacity: 0,
            ease: 'power2.out',
            stagger: 0.15,
            delay: 0.6
        });
    }
    
    // Trainer dashboard animations
    const trainerCards = document.querySelectorAll('.trainer-action-card');
    if (trainerCards.length > 0) {
        gsap.from(trainerCards, {
            duration: 0.8,
            y: 30,
            opacity: 0,
            ease: 'power2.out',
            stagger: 0.2,
            delay: 0.3
        });
    }
    
    // Activity items animation
    gsap.from('.activity-item', {
        duration: 0.5,
        x: -20,
        opacity: 0,
        ease: 'power2.out',
        stagger: 0.1,
        delay: 1
    });
}

// Dashboard card hover interactions
function initDashboardInteractions() {
    // Stat card interactions
    const statCards = document.querySelectorAll('.stat-card-dashboard');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                duration: 0.3,
                y: -5,
                boxShadow: '0 12px 24px rgba(15, 22, 33, 0.12)',
                ease: 'power2.out'
            });
            
            const icon = card.querySelector('.stat-card-icon');
            if (icon) {
                gsap.to(icon, {
                    duration: 0.3,
                    scale: 1.1,
                    rotation: 5,
                    ease: 'back.out(1.7)'
                });
            }
        });
        
        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                duration: 0.3,
                y: 0,
                boxShadow: 'var(--shadow-sm)',
                ease: 'power2.out'
            });
            
            const icon = card.querySelector('.stat-card-icon');
            if (icon) {
                gsap.to(icon, {
                    duration: 0.3,
                    scale: 1,
                    rotation: 0,
                    ease: 'power2.out'
                });
            }
        });
    });
    
    // Quick action button interactions
    const quickActions = document.querySelectorAll('.quick-action-btn');
    quickActions.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            gsap.to(btn.querySelector('i'), {
                duration: 0.2,
                x: 5,
                ease: 'power2.out'
            });
        });
        
        btn.addEventListener('mouseleave', () => {
            gsap.to(btn.querySelector('i'), {
                duration: 0.2,
                x: 0,
                ease: 'power2.out'
            });
        });
    });
}

// Initialize enhanced dashboard on DOM load
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('/dashboard')) {
        initEnhancedDashboard();
        initDashboardInteractions();
    }
});


// =========================================================
// JOURNEY MAP & FLOW VISUALIZATION ANIMATIONS
// =========================================================

function initJourneyMap() {
    const journeyMap = document.querySelector('.journey-map');
    if (!journeyMap) return;
    
    // Animate journey map entrance
    gsap.from('.journey-map', {
        duration: 0.8,
        y: 30,
        opacity: 0,
        ease: 'power2.out'
    });
    
    // Animate journey steps with stagger
    const journeySteps = document.querySelectorAll('.journey-step');
    gsap.from(journeySteps, {
        duration: 0.6,
        scale: 0,
        opacity: 0,
        ease: 'back.out(1.7)',
        stagger: 0.15,
        delay: 0.3
    });
    
    // Animate connectors
    gsap.from('.journey-step-connector', {
        duration: 0.8,
        scaleX: 0,
        transformOrigin: 'left',
        ease: 'power2.out',
        stagger: 0.15,
        delay: 0.6
    });
    
    // Add hover effect to journey steps
    journeySteps.forEach(step => {
        step.addEventListener('mouseenter', () => {
            const icon = step.querySelector('.journey-step-icon');
            if (icon) {
                gsap.to(icon, {
                    duration: 0.3,
                    scale: 1.15,
                    rotation: 5,
                    ease: 'back.out(1.7)'
                });
            }
        });
        
        step.addEventListener('mouseleave', () => {
            const icon = step.querySelector('.journey-step-icon');
            if (icon) {
                gsap.to(icon, {
                    duration: 0.3,
                    scale: 1,
                    rotation: 0,
                    ease: 'power2.out'
                });
            }
        });
    });
    
    // Animate current status message
    gsap.from('.journey-map .text-center.mt-4', {
        duration: 0.6,
        y: 20,
        opacity: 0,
        ease: 'power2.out',
        delay: 1.2
    });
}

// Timeline animations
function initTimeline() {
    const timeline = document.querySelector('.status-timeline');
    if (!timeline) return;
    
    const timelineItems = document.querySelectorAll('.timeline-item');
    
    gsap.from(timelineItems, {
        scrollTrigger: {
            trigger: timeline,
            start: 'top 80%',
            toggleActions: 'play none none reverse'
        },
        duration: 0.6,
        x: -20,
        opacity: 0,
        ease: 'power2.out',
        stagger: 0.15
    });
}

// Progress indicator animation
function initProgressIndicators() {
    const progressIndicators = document.querySelectorAll('.progress-indicator-fill');
    
    progressIndicators.forEach(indicator => {
        const targetWidth = indicator.style.width || '0%';
        
        gsap.from(indicator, {
            scrollTrigger: {
                trigger: indicator,
                start: 'top 85%',
                toggleActions: 'play none none reverse'
            },
            duration: 1.5,
            width: '0%',
            ease: 'power2.out'
        });
    });
}

// Initialize on membership page
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('/membership')) {
        initJourneyMap();
        initTimeline();
        initProgressIndicators();
    }
});