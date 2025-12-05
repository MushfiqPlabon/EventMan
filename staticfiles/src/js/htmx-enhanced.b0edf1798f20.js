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
                window.reactiveCore.showNotification(triggers.showMessage, 'success');
            }
            
            if (triggers.updateCount) {
                // Update participant counts
                document.querySelectorAll('[data-participant-count]').forEach(el => {
                    el.textContent = triggers.updateCount;
                });
            }
        }
    });
});
