import Swal from "sweetalert2";

// Reusable configuration function to reduce redundancy
function createConfirmConfig(
	title,
	text,
	icon = "warning",
	confirmColor = "#d33",
) {
	return {
		title: title,
		text: text,
		icon: icon,
		showCancelButton: true,
		confirmButtonColor: confirmColor,
		cancelButtonColor: "#888",
		confirmButtonText: "Continue",
		cancelButtonText: "Cancel",
	};
}

// Configuration map for different confirmation types - O(1) lookup
const confirmConfigMap = {
	rsvp: (eventName) => {
		const config = createConfirmConfig(
			"Confirm RSVP",
			`Are you sure you want to RSVP to "${eventName}"?`,
			"question",
			"#3085d6",
		);
		config.confirmButtonText = "Yes, RSVP me!";
		return config;
	},
	cancel_rsvp: (eventName) => {
		const config = createConfirmConfig(
			"Confirm Cancellation",
			`Are you sure you want to cancel your RSVP for "${eventName}"?`,
			"warning",
			"#d33",
		);
		config.confirmButtonText = "Yes, cancel RSVP";
		config.cancelButtonText = "Keep RSVP";
		return config;
	},
	delete: (itemType, itemName) => {
		const config = createConfirmConfig(
			`Delete ${itemType}?`,
			`Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
			"warning",
			"#d33",
		);
		config.confirmButtonText = `Yes, delete ${itemType.toLowerCase()}!`;
		return config;
	},
};

// Global function for RSVP confirmation
function confirmRSVP(eventName) {
	return Swal.fire(confirmConfigMap.rsvp(eventName));
}

// Global function for RSVP cancellation
function confirmCancelRSVP(eventName) {
	return Swal.fire(confirmConfigMap.cancel_rsvp(eventName));
}

// Global function for delete confirmation
function confirmDelete(itemType, itemName) {
	return Swal.fire(confirmConfigMap.delete(itemType, itemName));
}

// Global function for success messages
function showSuccess(title, text) {
	return Swal.fire({
		icon: "success",
		title: title,
		text: text,
		timer: 2000,
		showConfirmButton: false,
	});
}

// Global function for error messages
function showError(title, text) {
	return Swal.fire({
		icon: "error",
		title: title,
		text: text,
	});
}

// Make functions available globally
window.swalUtils = {
	confirmRSVP,
	confirmCancelRSVP,
	confirmDelete,
	showSuccess,
	showError,

	// Convenience methods for specific actions
	confirmRSVPAction: (eventName) => confirmRSVP(eventName),

	confirmCancelRSVPAction: (eventName) => confirmCancelRSVP(eventName),

	confirmDeleteAction: (itemType, itemName) =>
		confirmDelete(itemType, itemName),

	confirmDeleteWithSpinner: (itemType, itemName) =>
		confirmDelete(itemType, itemName),
};
