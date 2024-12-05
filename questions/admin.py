from django.contrib import admin
from .models import Tag, Question, QuestionTag, Answer, Comment

admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(QuestionTag)
admin.site.register(Answer)
admin.site.register(Comment)
