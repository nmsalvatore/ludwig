document.body.addEventListener("htmx:sseBeforeMessage", () => {
    const noPostsMessage = document.getElementById("no_posts_message");

    if (!noPostsMessage) {
        return;
    }

    noPostsMessage.remove();
});
