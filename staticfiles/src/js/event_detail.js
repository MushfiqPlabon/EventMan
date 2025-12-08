// Functions for event detail page

function showLoading(button) {
    const buttonText = button.querySelector('.button-text');
    const spinner = button.querySelector('.loading-spinner');
    if (buttonText && spinner) {
        buttonText.classList.add('hidden');
        spinner.classList.remove('hidden');
        button.disabled = true;
    }
}

function hideLoading(button) {
    const buttonText = button.querySelector('.button-text');
    const spinner = button.querySelector('.loading-spinner');
    if (buttonText && spinner) {
        buttonText.classList.remove('hidden');
        spinner.classList.add('hidden');
        button.disabled = false;
    }
}

function confirmDeleteWithSpinner(url, itemType, itemName) {
    window.swalUtils.confirmDeleteAction(itemType, itemName).then((result) => {
        if (result.isConfirmed) {
            // Show loading on delete button
            const deleteBtn = document.getElementById('delete-btn');
            showLoading(deleteBtn);
            // Redirect to the delete URL
            window.location.href = url;
        }
    });
}

function handleRsvpConfirmation(url, action, eventName) {
    // Show confirmation dialog based on the action - O(1) dictionary lookup
    const actionMap = {
        'cancel': () => window.swalUtils.confirmCancelRSVPAction(eventName),
        'add': () => window.swalUtils.confirmRSVPAction(eventName)
    };

    let confirmPromise = (actionMap[action] || actionMap['add'])();

    confirmPromise.then((result) => {
        if (result.isConfirmed) {
            // Show loading on RSVP button
            const rsvpBtn = document.getElementById('rsvp-btn');
            showLoading(rsvpBtn);

            // Submit the form via AJAX to avoid page refresh
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            }).then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    // Reload page to refresh the RSVP status
                    window.location.reload();
                }
            }).catch(error => {
                console.error('Error:', error);
                hideLoading(rsvpBtn);
                window.swalUtils.showError('Error', 'There was a problem with your request. Please try again.');
            });
        }
    });
}

// Make functions available globally if needed
window.eventDetailUtils = {
    showLoading,
    hideLoading,
    confirmDeleteWithSpinner,
    handleRsvpConfirmation
};