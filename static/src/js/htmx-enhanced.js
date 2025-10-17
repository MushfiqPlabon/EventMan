// Minimal HTMX enhancements for Tailwind CSS - 30 lines vs 422 lines
document.addEventListener('DOMContentLoaded', function() {
    // HTMX event listeners for enhanced UX
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        // Show loading state with Tailwind classes
        const target = evt.target;
        if (target.tagName === 'BUTTON') {
            target.disabled = true;
            target.dataset.originalText = target.innerHTML;
            target.innerHTML = '⏳ Loading...';
            target.classList.add('opacity-75', 'cursor-not-allowed');
        }
    });

    document.body.addEventListener('htmx:afterRequest', function(evt) {
        // Reset button state
        const target = evt.target;
        if (target.tagName === 'BUTTON' && target.dataset.originalText) {
            target.disabled = false;
            target.innerHTML = target.dataset.originalText;
            target.classList.remove('opacity-75', 'cursor-not-allowed');
        }
    });

    // Handle custom events from server
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        const xhr = evt.detail.xhr;
        const triggerHeader = xhr.getResponseHeader('HX-Trigger');
        
        if (triggerHeader) {
            const triggers = JSON.parse(triggerHeader);
            
            if (triggers.showMessage) {
                showNotification(triggers.showMessage, 'success');
            }
            
            if (triggers.updateCount) {
                // Update participant counts
                document.querySelectorAll('[data-participant-count]').forEach(el => {
                    el.textContent = triggers.updateCount;
                });
            }
        }
    });

    // Notification system using Tailwind classes
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const bgColor = type === 'success' ? 'bg-green-500' : 
                       type === 'error' ? 'bg-red-500' : 
                       type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500';
        
        notification.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-4 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200 text-xl">&times;</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    // Make showNotification available globally
    window.showNotification = showNotification;
});
