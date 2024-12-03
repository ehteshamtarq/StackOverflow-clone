from django import forms
from .models import Question, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Tags"
    )

    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']
