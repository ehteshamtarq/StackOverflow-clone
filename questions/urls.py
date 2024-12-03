from django.urls import path
from . import views


app_name = 'questions'


urlpatterns = [
    path('', views.QuestionListView.as_view(), name='question_list'),
    path('<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('new/', views.QuestionCreateView.as_view(), name='question_create'),
]
