from django import forms
from .models import Question, Tag, Answer, Comment


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

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['body']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

class QuestionEditDeleteForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'body']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'description']
