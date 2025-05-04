from django import forms

from .models import Dialogue


class DialogueCreationForm(forms.ModelForm):
    title = forms.CharField(max_length=200)
    summary = forms.CharField(widget=forms.Textarea, required=False)
    is_visible = forms.BooleanField(required=False, initial=False)
    is_open = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = Dialogue
        fields = ["title", "summary", "is_visible", "is_open"]
