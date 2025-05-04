from django import template
from django.utils.text import get_text_list

register = template.Library()

@register.filter
def text_list(values, last_word="and"):
    if hasattr(values, "all"):
        values = list(values)
    return get_text_list(values, last_word)
