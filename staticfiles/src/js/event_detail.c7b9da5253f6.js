// Functions for event detail page with enhanced loading indicators

function showLoading(buttonElement) {
	if (buttonElement) {
		// Find button elements within the container
		const buttonText =
			buttonElement.querySelector(".button-text") ||
			buttonElement.querySelector("span:not(.loading-spinner)");
		const spinner = buttonElement.querySelector(".loading-spinner");

		if (buttonText) {
			buttonText.classList.add("hidden");
		}
		if (spinner) {
			spinner.classList.remove("hidden");
		}

		buttonElement.disabled = true;
		buttonElement.classList.add("opacity-70", "cursor-not-allowed");
	}
}

function hideLoading(buttonElement) {
	if (buttonElement) {
		// Find button elements within the container
		const buttonText =
			buttonElement.querySelector(".button-text") ||
			buttonElement.querySelector("span:not(.loading-spinner)");
		const spinner = buttonElement.querySelector(".loading-spinner");

		if (buttonText) {
			buttonText.classList.remove("hidden");
		}
		if (spinner) {
			spinner.classList.add("hidden");
		}

		buttonElement.disabled = false;
		buttonElement.classList.remove("opacity-70", "cursor-not-allowed");
	}
}

function confirmDeleteWithSpinner(url, itemType, itemName) {
	window.swalUtils.confirmDeleteAction(itemType, itemName).then((result) => {
		if (result.isConfirmed) {
			// Show loading on delete button
			const deleteBtn = document.getElementById("delete-btn");
			if (deleteBtn) {
				showLoading(deleteBtn);
			}

			// Redirect to the delete URL
			window.location.href = url;
		}
	});
}

function handleRsvpConfirmation(url, action, eventName) {
	// Show confirmation dialog based on the action - O(1) dictionary lookup
	const actionMap = {
		cancel: () => window.swalUtils.confirmCancelRSVPAction(eventName),
		add: () => window.swalUtils.confirmRSVPAction(eventName),
	};

	const confirmPromise = (actionMap[action] || actionMap.add)();

	confirmPromise.then((result) => {
		if (result.isConfirmed) {
			// Show loading on RSVP button
			const rsvpBtn = document.getElementById("rsvp-btn");
			if (rsvpBtn) {
				showLoading(rsvpBtn);
			}

			// Submit the form via AJAX to avoid page refresh
			fetch(url, {
				method: "POST",
				headers: {
					"Content-Type": "application/x-www-form-urlencoded",
					"X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
						.value,
				},
			})
				.then(async (response) => {
					if (
						response.headers.get("Content-Type")?.includes("application/json")
					) {
						// Handle AJAX response from the enhanced RSVP
						const data = await response.json();
						if (data.success) {
							// Update the button text and class based on the new state
							if (rsvpBtn) {
								if (data.is_participant) {
									// Now a participant - change to cancel button
									rsvpBtn.className =
										"rsvp-cancel bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-md transition duration-300 focus:outline-none focus:ring-2 focus:ring-red-400";
									rsvpBtn.onclick = () => {
										handleRsvpConfirmation(url, "cancel", eventName);
									};
									rsvpBtn.innerHTML =
										'<span class="button-text">Cancel RSVP</span><span class="loading-spinner hidden">Canceling...</span>';
									rsvpBtn.setAttribute(
										"aria-label",
										`Cancel your RSVP for ${eventName}`,
									);

									// Show success message
									window.swalUtils.showSuccess("RSVP Successful", data.message);
								} else {
									// Not a participant anymore - change to RSVP button
									rsvpBtn.className =
										"bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-md transition duration-300 focus:outline-none focus:ring-2 focus:ring-green-400";
									rsvpBtn.onclick = () => {
										handleRsvpConfirmation(url, "add", eventName);
									};
									rsvpBtn.innerHTML =
										'<span class="button-text">RSVP to Event</span><span class="loading-spinner hidden">RSVPing...</span>';
									rsvpBtn.setAttribute("aria-label", `RSVP to ${eventName}`);

									// Show info message
									window.swalUtils.showInfo("RSVP Cancelled", data.message);
								}

								// Update participant count display
								const participantCountEl = document.querySelector(
									'[id="participants-count"]',
								);
								if (participantCountEl) {
									participantCountEl.innerText = `${data.participant_count} participants`;
								}

								const participantTextEl = document.querySelector(
									'[id="participant-text"]',
								);
								if (participantTextEl) {
									if (data.participant_count > 0) {
										participantTextEl.innerText = `This event has ${data.participant_count} participants.`;
									} else {
										participantTextEl.innerText = "No participants yet.";
									}
								}
							}
						} else {
							// Show error message from server
							window.swalUtils.showError(
								"Error",
								data.message || "An error occurred processing your RSVP",
							);
						}
					} else if (response.redirected) {
						// For non-AJAX responses, redirect as before
						window.location.href = response.url;
					} else {
						// For non-AJAX responses, reload page to refresh the RSVP status
						window.location.reload();
					}
				})
				.catch((error) => {
					console.error("Error:", error);
					if (rsvpBtn) {
						hideLoading(rsvpBtn);
					}
					window.swalUtils.showError(
						"Request Error",
						"There was a problem processing your request. Please refresh the page and try again. If the problem persists, contact support.",
					);
				});
		}
	});
}

// Generic loading indicator function for forms
function showFormLoading(formId) {
	const form = document.getElementById(formId);
	if (form) {
		const submitBtn = form.querySelector('button[type="submit"]');
		if (submitBtn) {
			// Create a loading element if it doesn't exist
			let loadingElement = form.querySelector(".form-loading");
			if (!loadingElement) {
				loadingElement = document.createElement("div");
				loadingElement.className = "form-loading mt-4 text-center hidden";
				loadingElement.innerHTML = `
					<div class="inline-block animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500"></div>
					<span class="ml-2">Processing your request...</span>
				`;
				form.appendChild(loadingElement);
			}

			// Disable submit button and show loading
			submitBtn.disabled = true;
			submitBtn.classList.add("opacity-70", "cursor-not-allowed");
			loadingElement.classList.remove("hidden");
		}
	}
}

function hideFormLoading(formId) {
	const form = document.getElementById(formId);
	if (form) {
		const submitBtn = form.querySelector('button[type="submit"]');
		if (submitBtn) {
			submitBtn.disabled = false;
			submitBtn.classList.remove("opacity-70", "cursor-not-allowed");
		}

		const loadingElement = form.querySelector(".form-loading");
		if (loadingElement) {
			loadingElement.classList.add("hidden");
		}
	}
}

// Make functions available globally if needed
window.eventDetailUtils = {
	showLoading,
	hideLoading,
	confirmDeleteWithSpinner,
	handleRsvpConfirmation,
	showFormLoading,
	hideFormLoading,
};
