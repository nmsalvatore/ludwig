from enum import StrEnum


class TemplateName(StrEnum):
    # full page templates
    CREATE_DIALOGUE = "dialogues/create_dialogue.html"
    DIALOGUE_DETAIL = "dialogues/dialogue_detail.html"

    # partial templates
    PERMISSION_DENIED = "dialogues/partials/403.html"
    DIALOGUE_SETTINGS = "dialogues/partials/settings.html"
    POLLING = "dialogues/partials/polling.html"
    POST_DETAIL = "dialogues/partials/post_detail.html"
    POST_FORM = "dialogues/partials/post_form.html"
    TOGGLE_VISIBILITY = "dialogues/partials/toggle_visibility.html"
    USER_SEARCH_RESULTS = "dialogues/partials/user_search_results.html"
