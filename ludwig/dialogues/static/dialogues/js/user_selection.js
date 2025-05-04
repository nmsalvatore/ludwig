document.addEventListener("click", function (e) {
    if (e.target && e.target.classList.contains("user-option")) {
        const userId = e.target.dataset.userId;
        const username = e.target.textContent.trim();

        // check if user is already selected
        if (!document.querySelector(`input[value="${userId}"]`)) {
            // create html for selected user
            const selectedUser = document.createElement("div");
            selectedUser.className = "selected-user";
            selectedUser.innerHTML = `
                <span>${username}</span>
                <button type="button" class="remove-user">×</button>
                <input type="hidden" name="selected_participants" value="${userId}">
            `;

            // add user to selected_users
            document.getElementById("selected_users").appendChild(selectedUser);

            // clear search input and results
            document.getElementById("user_search").value = "";
            document.getElementById("search_results").innerHTML = "";
        }
    }

    // remove selected user
    if (e.target && e.target.classList.contains("remove-user")) {
        e.target.closest(".selected-user").remove();
    }
});
