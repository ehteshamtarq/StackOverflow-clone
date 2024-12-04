from django.urls import path
from . import views


app_name = 'questions'


urlpatterns = [
    path('questions/', views.QuestionListView.as_view(), name='question_list'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('questions/new/', views.QuestionCreateView.as_view(), name='question_create'),
    path('tags/', views.TagListView.as_view(), name='tag_list'),
]
