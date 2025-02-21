const helpTexts = {
    "help-display-duration": "Set the display duration in HH:MM:SS format.",
    "help-full-screen": "Enable full-screen mode for better viewing.",
    "help-local-files": "Enable this to use only locally stored files.",
    "help-max-files": "Set the maximum number of saved image files.",
    "help-bg-color": "Choose the background color for the display.",
    "help-theme": "Select the active theme for the display.",
    "help-style": "Choose the active style from the available options."
};

function openModal(helpKey) {
    document.getElementById("modal-title").textContent = "Help";
    document.getElementById("modal-text").textContent = helpTexts[helpKey];
    document.getElementById("modal-container").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("modal-container").classList.add("hidden");
}

function showError(message) {
    document.getElementById("error-message").textContent = message;
    document.getElementById("error-modal").classList.remove("hidden");
}

function closeErrorModal() {
    document.getElementById("error-modal").classList.add("hidden");
}

document.getElementById("updateBtn").addEventListener("click", function () {
    const data = {
        display_duration: document.getElementById("display_duration").value,
        full_screen: document.getElementById("full_screen").checked,
        local_files_only: document.getElementById("local_files_only").checked,
        max_num_saved_files: parseInt(document.getElementById("max_num_saved_files").value),
        background_color: document.getElementById("background_color").value,
        active_theme: document.getElementById("active_theme").value,
        active_style: document.getElementById("active_style").value
    };

    fetch("/update_config", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            } else {
                alert(data.message);  // Success feedback
            }
        })
        .catch(() => showError("Network error. Please try again."));
});


document.getElementById("cancelBtn").addEventListener("click", function () {
    location.reload();
});

