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
        const searchInput = document.getElementById('search_query');
        const statusFilter = document.getElementById('filter_status');
        const categoryFilter = document.getElementById('filter_category');
        
        if (!searchInput) return;

        let debounceTimer;
        const performSearch = () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.performLiveFilter();
            }, 300);
        };

        searchInput.addEventListener('input', performSearch);
        if (statusFilter) statusFilter.addEventListener('change', performSearch);
        if (categoryFilter) categoryFilter.addEventListener('change', performSearch);
    }

    async performLiveFilter() {
        const searchInput = document.getElementById('search_query');
        const statusFilter = document.getElementById('filter_status');
        const categoryFilter = document.getElementById('filter_category');
        const eventsContainer = document.getElementById('events-container');
        
        if (!eventsContainer) return;

        const params = new URLSearchParams({
            q: searchInput?.value || '',
            status: statusFilter?.value || '',
            category: categoryFilter?.value || '',
            ajax: '1'
        });

        this.showLoading(eventsContainer, true);

        try {
            const response = await fetch(`/events/ajax/?${params}`);
            const data = await response.json();
            
            // Smooth transition
            eventsContainer.style.opacity = '0.3';
            setTimeout(() => {
                eventsContainer.innerHTML = data.html;
                eventsContainer.style.opacity = '1';
                this.showLoading(eventsContainer, false);
                this.showNotification(`Found ${eventsContainer.querySelectorAll('[data-event-id]').length} events`, 'info');
            }, 150);

        } catch (error) {
            console.error('Search failed:', error);
            this.showLoading(eventsContainer, false);
            this.showNotification('Search failed. Please try again.', 'error');
        }
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
            feedback.className = 'field-feedback text-sm mt-1 transition-all duration-200';
            input.parentNode.appendChild(feedback);
        }
        
        feedback.textContent = message;
        feedback.className = `field-feedback text-sm mt-1 transition-all duration-200 ${
            isValid ? 'text-green-600' : 'text-red-600'
        }`;
        
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

    showLoading(container, show) {
        if (show) {
            container.style.opacity = '0.5';
            container.style.pointerEvents = 'none';
        } else {
            container.style.opacity = '1';
            container.style.pointerEvents = 'auto';
        }
    }

    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 text-white transform translate-x-full transition-transform duration-300 ${
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
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(full)';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.reactiveCore = new ReactiveCore();
});
