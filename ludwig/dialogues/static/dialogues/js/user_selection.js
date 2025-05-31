document.addEventListener("click", function (e) {
    if (e.target && e.target.classList.contains("user-option")) {
        const userId = e.target.dataset.userId;
        const username = e.target.textContent.trim();

        if (!document.querySelector(`input[value="${userId}"]`)) {
            // create html for selected user
            const selectedUser = document.createElement("div");
            selectedUser.className = "selected-user";
            selectedUser.innerHTML = `
                <span>${username}</span>
                <button type="button" class="remove-user">×</button>
                <input type="hidden" name="participants" value="${userId}">
            `;

            document.getElementById("selected_users").appendChild(selectedUser);
            document.getElementById("user_search").value = "";
            document.getElementById("search_results").innerHTML = "";
        }
    }

    if (e.target && e.target.classList.contains("remove-user")) {
        e.target.closest(".selected-user").remove();
    }
});
