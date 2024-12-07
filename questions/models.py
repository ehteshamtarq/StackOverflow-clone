from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    is_closed = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_answers')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer by {self.user.username} for '{self.question.title}'"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE, related_name='question_comments')
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE, related_name='answer_comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question', 'answer')  # Enforce one comment per user per question/answer

    def __str__(self):
        if self.question:
            return f"Comment by {self.user.username} on Question '{self.question.title}'"
        elif self.answer:
            return f"Comment by {self.user.username} on Answer '{self.answer.body[:30]}...'"

class QuestionTag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='questions')

    class Meta:
        unique_together = ('question', 'tag')

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=10, choices=(('upvote', 'Upvote'), ('downvote', 'Downvote')))

    class Meta:
        unique_together = ('user', 'question')
