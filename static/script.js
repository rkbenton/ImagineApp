document.getElementById("updateBtn").addEventListener("click", function() {
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    }).then(response => response.json())
      .then(data => alert(data.message));
});

document.getElementById("cancelBtn").addEventListener("click", function() {
    location.reload();
});
