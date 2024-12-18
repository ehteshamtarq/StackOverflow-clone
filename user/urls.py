from django.urls import path
from .import views
from django.contrib.auth import views as auth_views


app_name = 'user'

urlpatterns = [

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user/logout.html'), name='logout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('', views.main, name='main'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.  search_view, name='search_view'),
]
