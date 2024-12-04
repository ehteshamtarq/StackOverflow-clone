from django.contrib import admin
from .models import Tag, Question, QuestionTag

admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(QuestionTag)