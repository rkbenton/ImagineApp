const helpTexts = {
    "help-display-duration": "Set the display duration in HH:MM:SS format.",
    "help-full-screen": "Enable full-screen mode for better viewing.",
    "help-local-files": "Enable this to use only locally stored files.",
    "help-max-files": "Set the maximum number of saved image files.",
    "help-bg-color": "Choose the background color for the display.",
    "help-theme": "Select the active theme for the display.",
    "help-style": "Choose the active style from the available options.",
    "help-min-rating": "Minimum rating filter for local-files-only slideshow."
};

function openModal(helpId) {
  // Get the help modal container and its content elements
  var modalContainer = document.getElementById("modal-container");
  var modalTitle = document.getElementById("modalTitle");
  var modalText = document.getElementById("modal-text");

  // Set modal content based on helpId
  switch (helpId) {
    case "help-display-duration":
      modalTitle.textContent = "Display Duration Help";
      modalText.textContent = "This setting controls how long each slide is displayed.";
      break;
    case "help-full-screen":
      modalTitle.textContent = "Full Screen Help";
      modalText.textContent = "Toggle full screen mode for the display.";
      break;
    case "help-local-files":
      modalTitle.textContent = "Local Files Only Help";
      modalText.textContent = "Restrict the slideshow to local files only.";
      break;
    case "help-min-rating":
      modalTitle.textContent = "Minimum Rating Help";
      modalText.textContent = "Set the minimum rating for files to be included in the slideshow.";
      break;
    case "help-max-files":
      modalTitle.textContent = "Max Num Saved Files Help";
      modalText.textContent = "This setting controls the maximum number of files that can be saved.";
      break;
    case "help-bg-color":
      modalTitle.textContent = "Background Color Help";
      modalText.textContent = "Choose a background color for the display.";
      break;
    case "help-theme":
      modalTitle.textContent = "Active Theme Help";
      modalText.textContent = "Select the active theme from the dropdown.";
      break;
    case "help-style":
      modalTitle.textContent = "Active Style Help";
      modalText.textContent = "Select the style to apply to the display.";
      break;
    default:
      modalTitle.textContent = "Help";
      modalText.textContent = "";
  }

  // Use Bootstrap's modal API to show the modal
  var modal = new bootstrap.Modal(modalContainer);
  modal.show();
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
    const themeDropdown = document.getElementById("active_theme");

    const data = {
        display_duration: document.getElementById("display_duration").value,
        full_screen: document.getElementById("full_screen").checked,
        local_files_only: document.getElementById("local_files_only").checked,
        max_num_saved_files: parseInt(document.getElementById("max_num_saved_files").value),
        background_color: document.getElementById("background_color").value,
        theme_display_name: themeDropdown.value, // This is the display_name
        active_style: document.getElementById("active_style").value,
        minimum_rating_filter: parseFloat( document.getElementById("minimum_rating_filter").value)
    };

    console.log("about to call POST /update_config with:");
    console.log(JSON.stringify(data, null, 2));

    fetch("/update_config", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.log("Error occurred: " + data.error);
                showError(data.error);
            } else {
                console.log("Successfully updated config");
                alert(data.message);  // Success feedback
            }
        })
        .catch(() => showError("Network error. Please try again."));
});


// Update styles dropdown dynamically when the theme changes
document.getElementById("active_theme").addEventListener("change", function () {
    const selectedTheme = this.value;
    const stylesDropdown = document.getElementById("active_style");

    fetch(`/get_styles?theme=${selectedTheme}`)
        .then(response => response.json())
        .then(styles => {
            stylesDropdown.innerHTML = "";  // Clear current options
            for (const style of styles) {
                let option = document.createElement("option");
                option.value = style;
                option.textContent = style;
                stylesDropdown.appendChild(option);
            }
        })
        .catch(() => showError("Failed to load styles for this theme."));
});


document.getElementById("revertBtn").addEventListener("click", function (event) {
    event.preventDefault()
    location.href = location.href;
    return false;
});

