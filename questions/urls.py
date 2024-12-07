from django.urls import path
from . import views


app_name = 'questions'


urlpatterns = [
    path('questions/', views.QuestionListView.as_view(), name='question_list'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('questions/new/', views.QuestionCreateView.as_view(), name='question_create'),
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('questions/<int:question_id>/vote/<str:vote_type>/', views.VoteQuestionView.as_view(), name='vote_question'),
    path('question/<int:pk>/edit/', views.EditQuestionView.as_view(), name='edit_question'),
    path('question/<int:pk>/delete/', views.DeleteQuestionView.as_view(), name='delete_question'),
    path('answer/<int:pk>/edit/', views.EditAnswerView.as_view(), name='edit_answer'),
    path('answer/<int:pk>/delete/', views.DeleteAnswerView.as_view(), name='delete_answer'),
    path('comment/<int:pk>/delete/', views.DeleteCommentView.as_view(), name='delete_comment'),
]
