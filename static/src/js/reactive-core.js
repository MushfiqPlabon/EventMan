// Ultra-efficient reactive core for Django MVT
class ReactiveCore {
    constructor() {
        this.init();
    }

    init() {
        this.setupCSRF();
        this.setupLiveSearch();
        this.setupLiveRSVP();
        this.setupLiveDashboard();
        this.setupFormEnhancements();
        this.setupLoadingStates();
        this.setupMicroInteractions();
        this.setupPageTransitions();
        this.setupProgressBar();
        
        // Enhanced interactivity and animations
        this.setupInteractiveElements();
        this.setupAnimationObservers();
    }

    setupCSRF() {
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                        document.querySelector('meta[name="csrf-token"]')?.content ||
                        this.getCookie('csrftoken');
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    setupLiveSearch() {
        // HTMX will handle live search directly on the form
        // Ensure the search form in event_list.html has hx-get, hx-target, hx-trigger, and hx-indicator attributes.
    }

    setupLiveSearch() {
        // HTMX will handle live search directly on the form
    }

    setupLiveRSVP() {
        document.addEventListener('click', async (e) => {
            if (e.target.matches('[data-rsvp-toggle]')) {
                e.preventDefault();
                await this.toggleRSVP(e.target);
            }
        });
    }

    async toggleRSVP(button) {
        const eventId = button.dataset.eventId;
        const wasRSVPed = button.dataset.rsvped === 'true';
        
        // Optimistic UI update
        button.disabled = true;
        const originalContent = button.innerHTML;
        button.innerHTML = '⏳ Processing...';

        try {
            const response = await fetch(`/events/${eventId}/rsvp_toggle/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json',
                },
            });

            const data = await response.json();
            
            if (data.success) {
                // Update button state
                button.dataset.rsvped = data.rsvped;
                button.innerHTML = data.rsvped ? '✅ RSVP\'d' : '📝 RSVP';
                button.className = button.className.replace(/(btn-success|btn-primary)/, 
                    data.rsvped ? 'btn-success' : 'btn-primary');
                
                // Update participant count with animation
                const countElement = document.querySelector(`[data-event-${eventId}-count]`);
                if (countElement) {
                    this.animateNumber(countElement, 
                        parseInt(countElement.textContent), 
                        data.participant_count);
                }

                // Show success notification
                this.showNotification(data.message || 
                    (data.rsvped ? 'RSVP confirmed!' : 'RSVP cancelled'), 'success');

                // Add visual celebration for RSVP
                if (data.rsvped) {
                    this.celebrateRSVP(button);
                }

            } else {
                throw new Error(data.error || 'RSVP failed');
            }

        } catch (error) {
            console.error('RSVP failed:', error);
            button.innerHTML = originalContent;
            this.showNotification('RSVP failed. Please try again.', 'error');
        } finally {
            button.disabled = false;
        }
    }

    celebrateRSVP(button) {
        // Add confetti effect
        const confetti = document.createElement('div');
        confetti.innerHTML = '🎉';
        confetti.className = 'absolute text-2xl animate-bounce';
        confetti.style.left = '50%';
        confetti.style.top = '-20px';
        confetti.style.transform = 'translateX(-50%)';
        
        button.style.position = 'relative';
        button.appendChild(confetti);
        
        setTimeout(() => confetti.remove(), 1000);
    }

    setupLiveDashboard() {
        if (window.location.pathname.includes('dashboard')) {
            // Start live updates
            this.dashboardUpdateInterval = setInterval(() => this.updateDashboardStats(), 30000);
            
            // Update immediately
            setTimeout(() => this.updateDashboardStats(), 1000);
        }
    }

    async updateDashboardStats() {
        try {
            const response = await fetch('/dashboard/stats/?ajax=1');
            const data = await response.json();
            
            Object.entries(data).forEach(([key, value]) => {
                const element = document.querySelector(`[data-stat="${key}"]`);
                if (element) {
                    this.animateNumber(element, parseInt(element.textContent), value);
                }
            });

            // Update status indicator
            const statusElement = document.getElementById('live-status');
            if (statusElement) {
                statusElement.textContent = 'Just updated';
                statusElement.parentElement.className = statusElement.parentElement.className
                    .replace('bg-red-100', 'bg-green-100')
                    .replace('dark:bg-red-900', 'dark:bg-green-900');
            }

        } catch (error) {
            console.error('Dashboard update failed:', error);
            const statusElement = document.getElementById('live-status');
            if (statusElement) {
                statusElement.textContent = 'Update failed';
                statusElement.parentElement.className = statusElement.parentElement.className
                    .replace('bg-green-100', 'bg-red-100')
                    .replace('dark:bg-green-900', 'dark:bg-red-900');
            }
        }
    }

    animateNumber(element, from, to) {
        if (from === to) return;
        
        const duration = 1000;
        const start = Date.now();
        
        const animate = () => {
            const progress = Math.min((Date.now() - start) / duration, 1);
            const current = Math.floor(from + (to - from) * progress);
            element.textContent = current;
            
            if (progress < 1) requestAnimationFrame(animate);
        };
        animate();
    }

    setupFormEnhancements() {
        document.querySelectorAll('input, textarea, select').forEach(input => {
            input.classList.add('input-focus-effect');
            // Real-time validation
            input.addEventListener('input', () => this.validateField(input));
            input.addEventListener('blur', () => this.validateField(input));
            
            // Auto-save for forms with data-autosave
            let saveTimer;
            input.addEventListener('input', () => {
                const form = input.closest('form');
                if (form?.dataset.autosave) {
                    clearTimeout(saveTimer);
                    saveTimer = setTimeout(() => this.autoSave(form), 2000);
                }
            });

            // Enhanced focus states
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('ring-2', 'ring-blue-200', 'ring-opacity-50');
            });
            
            input.addEventListener('blur', () => {
                input.parentElement.classList.remove('ring-2', 'ring-blue-200', 'ring-opacity-50');
            });
        });
    }

    async autoSave(form) {
        const formData = new FormData(form);
        try {
            const response = await fetch(form.action + '?autosave=1', {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': this.csrfToken }
            });
            
            if (response.ok) {
                this.showNotification('Draft saved', 'success', 1500);
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }

    validateField(input) {
        const value = input.value.trim();
        let isValid = true;
        let message = '';

        // Email validation
        if (input.type === 'email' && value) {
            isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            message = isValid ? '✓ Valid email' : '✗ Invalid email format';
        }

        // Required field validation
        if (input.required && !value) {
            isValid = false;
            message = '✗ This field is required';
        }

        // Password strength
        if (input.type === 'password' && value) {
            const strength = this.getPasswordStrength(value);
            message = `Password strength: ${strength.text}`;
            isValid = strength.score >= 3;
        }

        this.showFieldValidation(input, isValid, message);
    }

    getPasswordStrength(password) {
        let score = 0;
        if (password.length >= 8) score++;
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/\d/.test(password)) score++;
        if (/[^a-zA-Z\d]/.test(password)) score++;

        const strengths = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        return { score, text: strengths[score] || 'Very Weak' };
    }

    showFieldValidation(input, isValid, message) {
        let feedback = input.parentNode.querySelector('.field-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'field-feedback text-sm mt-1 transition-all duration-200 animate-fade-in-down';
            input.parentNode.appendChild(feedback);
        }
        
        feedback.textContent = message;
        feedback.className = `field-feedback text-sm mt-1 transition-all duration-200 ${
            isValid ? 'text-green-600' : 'text-red-600'
        }`;
        
        // Add fade-out animation when message is removed or changed
        if (!message && feedback.textContent) {
            feedback.classList.add('animate-fade-out-up');
            feedback.addEventListener('animationend', () => feedback.remove(), { once: true });
        } else if (message && feedback.classList.contains('animate-fade-out-up')) {
            feedback.classList.remove('animate-fade-out-up');
            feedback.classList.add('animate-fade-in-down');
        }
        
        // Update input border
        input.className = input.className.replace(/(border-red-500|border-green-500|border-gray-300)/, '') +
                         (isValid && message ? ' border-green-500' : 
                          !isValid ? ' border-red-500' : ' border-gray-300');
    }

    setupLoadingStates() {
        document.addEventListener('submit', (e) => {
            const button = e.target.querySelector('button[type="submit"]');
            if (button && !button.dataset.noLoading) {
                button.disabled = true;
                button.dataset.originalText = button.innerHTML;
                button.innerHTML = '⏳ Processing...';
                
                // Reset after 10 seconds as fallback
                setTimeout(() => {
                    button.disabled = false;
                    button.innerHTML = button.dataset.originalText;
                }, 10000);
            }
        });
    }

    setupMicroInteractions() {
        // Hover effects for cards
        document.addEventListener('mouseover', (e) => {
            if (e.target.closest('.card-hover')) {
                e.target.closest('.card-hover').style.transform = 'translateY(-2px) scale(1.02)';
            }
        });

        document.addEventListener('mouseout', (e) => {
            if (e.target.closest('.card-hover')) {
                e.target.closest('.card-hover').style.transform = 'translateY(0) scale(1)';
            }
        });

        // Button click effects
        document.addEventListener('click', (e) => {
            if (e.target.matches('button, .btn-primary, .btn-success, .btn-danger')) {
                e.target.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    e.target.style.transform = 'scale(1)';
                }, 100);
            }
        });
    }

    setupPageTransitions() {
        const mainContent = document.querySelector('main');
        if (!mainContent) return;

        // On page load, add entry animation
        mainContent.classList.add('page-enter');

        // On navigation away, add exit animation with delay
        document.querySelectorAll('a').forEach(link => {
            if (!link.hasAttribute('hx-get') && !link.hasAttribute('hx-post') && !link.hasAttribute('hx-delete') && !link.hasAttribute('hx-put')) {
                link.addEventListener('click', (e) => {
                    const href = link.getAttribute('href');
                    if (href && href.startsWith('/') && !href.startsWith('#')) { // Only internal links
                        e.preventDefault();
                        mainContent.classList.remove('page-enter');
                        mainContent.classList.add('page-exit');
                        setTimeout(() => {
                            window.location.href = href;
                        }, 300); // Match fade-out animation duration
                    }
                });
            }
        });

        // Clean up entry animation after it completes
        mainContent.addEventListener('animationend', (e) => {
            if (e.animationName.includes('fade-in')) {
                mainContent.classList.remove('page-enter');
            }
        }, { once: true });
    }

    setupProgressBar() {
        const progressBar = document.getElementById('global-progress-bar');
        if (!progressBar) return;

        document.body.addEventListener('htmx:beforeRequest', () => {
            progressBar.style.width = '0%';
            progressBar.style.opacity = '1';
            progressBar.style.transition = 'width 0.1s ease-out, opacity 0.3s ease-out';
            progressBar.style.width = '30%'; // Start progress
        });

        document.body.addEventListener('htmx:afterRequest', () => {
            progressBar.style.width = '100%';
            progressBar.style.opacity = '0';
            progressBar.style.transition = 'width 0.3s ease-out, opacity 0.5s ease-out';
            setTimeout(() => {
                progressBar.style.width = '0%';
            }, 500); // Reset after fade out
        });

        document.body.addEventListener('htmx:onLoadError', () => {
            progressBar.style.width = '100%';
            progressBar.style.backgroundColor = 'red'; // Indicate error
            progressBar.style.opacity = '0';
            progressBar.style.transition = 'width 0.3s ease-out, opacity 0.5s ease-out';
            setTimeout(() => {
                progressBar.style.width = '0%';
                progressBar.style.backgroundColor = ''; // Reset color
            }, 500);
        });
    }

    showLoading(container, show, skeletonHtml = null) {
        if (show) {
            container.dataset.originalContent = container.innerHTML; // Store original content
            if (skeletonHtml) {
                container.innerHTML = skeletonHtml;
            }
            container.classList.add('skeleton-placeholder');
            container.style.pointerEvents = 'none';
        } else {
            if (container.dataset.originalContent) {
                container.innerHTML = container.dataset.originalContent; // Restore original content
                delete container.dataset.originalContent;
            }
            container.classList.remove('skeleton-placeholder');
            container.style.pointerEvents = 'auto';
        }
    }

    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 text-white transform translate-x-full transition-transform duration-300 animate-fade-in-right ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 
            type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
        }`;
        notification.innerHTML = `
            <div class="flex items-center space-x-2">
                <span>${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}</span>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white hover:text-gray-200">×</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            notification.classList.add('animate-fade-out-right');
            setTimeout(() => notification.remove(), 500); // Match fade-out duration
        }, duration);
    }

    // Enhanced interactivity for all UI elements
    setupInteractiveElements() {
        // Intersection Observer for fade-in animations
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                    entry.target.style.animationDelay = Math.random() * 200 + 'ms';
                }
            });
        }, { threshold: 0.1 });

        // Auto-enhance interactive elements
        document.addEventListener('DOMContentLoaded', () => {
            this.enhanceAllInteractiveElements();
        });

        // Enhance dynamically loaded content
        document.addEventListener('htmx:afterSwap', () => {
            this.enhanceAllInteractiveElements();
        });
    }

    enhanceAllInteractiveElements() {
        // Enhance buttons
        document.querySelectorAll('button:not([data-enhanced])').forEach(btn => {
            btn.setAttribute('data-enhanced', 'true');
            
            // Add ripple effect
            btn.addEventListener('click', (e) => {
                this.createRippleEffect(e, btn);
            });
            
            // Add loading states for form buttons
            if (btn.type === 'submit') {
                btn.addEventListener('click', () => {
                    btn.classList.add('opacity-75', 'cursor-not-allowed');
                    btn.disabled = true;
                    
                    // Re-enable after 3 seconds (fallback)
                    setTimeout(() => {
                        btn.classList.remove('opacity-75', 'cursor-not-allowed');
                        btn.disabled = false;
                    }, 3000);
                });
            }
        });

        // Enhance links
        document.querySelectorAll('a:not([data-enhanced])').forEach(link => {
            link.setAttribute('data-enhanced', 'true');
            
            // Add progressive loading
            link.addEventListener('mouseenter', () => {
                link.classList.add('scale-105', 'shadow-lg');
            });
            
            link.addEventListener('mouseleave', () => {
                link.classList.remove('scale-105', 'shadow-lg');
            });
        });

        // Enhance form inputs
        document.querySelectorAll('input, textarea, select').forEach(input => {
            if (input.getAttribute('data-enhanced')) return;
            input.setAttribute('data-enhanced', 'true');
            
            // Focus animations
            input.addEventListener('focus', () => {
                input.parentElement?.classList.add('ring-2', 'ring-primary/20');
                input.classList.add('scale-[1.01]');
            });
            
            input.addEventListener('blur', () => {
                input.parentElement?.classList.remove('ring-2', 'ring-primary/20');
                input.classList.remove('scale-[1.01]');
            });
            
            // Real-time validation feedback
            input.addEventListener('input', () => {
                if (input.checkValidity()) {
                    input.classList.remove('border-red-500');
                    input.classList.add('border-green-500');
                } else if (input.value) {
                    input.classList.remove('border-green-500');
                    input.classList.add('border-red-500');
                }
            });
        });

        // Enhance cards and containers
        document.querySelectorAll('.card, [class*="card"], .container, [class*="container"]').forEach(el => {
            if (el.getAttribute('data-enhanced')) return;
            el.setAttribute('data-enhanced', 'true');
            
            // Observe for intersection animations
            this.observer.observe(el);
            
            // Add hover effects
            el.addEventListener('mouseenter', () => {
                el.style.transform = 'translateY(-2px)';
                el.style.transition = 'transform 0.2s ease-out';
            });
            
            el.addEventListener('mouseleave', () => {
                el.style.transform = 'translateY(0)';
            });
        });

        // Enhance navigation items
        document.querySelectorAll('nav a, .nav-link').forEach(navLink => {
            if (navLink.getAttribute('data-enhanced')) return;
            navLink.setAttribute('data-enhanced', 'true');
            
            navLink.addEventListener('click', () => {
                // Add active state animation
                navLink.classList.add('animate-pulse');
                setTimeout(() => navLink.classList.remove('animate-pulse'), 600);
            });
        });
    }

    createRippleEffect(event, element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 600ms linear;
            pointer-events: none;
        `;
        
        // Add ripple keyframes if not exists
        if (!document.querySelector('#ripple-style')) {
            const style = document.createElement('style');
            style.id = 'ripple-style';
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    setupAnimationObservers() {
        // Performance-optimized animation observer
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    
                    // Stagger animations for multiple elements
                    const delay = Array.from(target.parentElement?.children || [])
                        .indexOf(target) * 100;
                    
                    setTimeout(() => {
                        target.classList.add('animate-fade-in');
                        target.style.opacity = '1';
                    }, delay);
                    
                    animationObserver.unobserve(target);
                }
            });
        }, { 
            threshold: 0.1,
            rootMargin: '50px'
        });

        // Observe elements that should animate in
        document.querySelectorAll(
            '.card, .event-card, .category-item, .dashboard-stat, .profile-card'
        ).forEach(el => {
            el.style.opacity = '0';
            animationObserver.observe(el);
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.reactiveCore = new ReactiveCore();
});
