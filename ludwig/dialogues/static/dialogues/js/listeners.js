document.addEventListener("DOMContentLoaded", () => {
    setPostFormListeners();
    setDeleteDialogueListeners();
});

document.addEventListener("htmx:afterOnLoad", () => {
    const postsContainer = document.getElementById("posts_container");
    const posts = postsContainer.querySelectorAll(".post");

    if (posts.length !== 0) {
        const noPostsMessage = document.getElementById("no_posts_message");
        if (noPostsMessage) {
            noPostsMessage.remove();
        }
    }
});

function setPostFormListeners() {
    const postForm = document.getElementById("post_form");

    if (!postForm) {
        return;
    }

    postForm.addEventListener("htmx:afterOnLoad", (event) => {
        if (event.detail.successful) {
            postForm.reset();
            postForm.focus();
        }
    });

    postForm.addEventListener("htmx:beforeRequest", () => {
        window.pausePolling = true;
    });

    postForm.addEventListener("htmx:afterRequest", () => {
        setTimeout(() => {
            window.pausePolling = false;
        }, 3000);
    });
}

function setDeleteDialogueListeners() {
    const deleteDialogueButton = document.getElementById(
        "delete_dialogue_button",
    );

    if (!deleteDialogueButton) {
        return;
    }

    deleteDialogueButton.addEventListener("click", () => {
        const dialog = document.getElementById("delete_dialogue_dialog");
        dialog.showModal();
    });
}
