from django.urls import path
from Guest import views

app_name = 'Guest'

urlpatterns = [
    path('', views.HomePage, name='homepage'),
    path('Login/', views.Login, name='login'),
    path('UserRegistration/', views.UserRegistration, name='user_registration'),
    path('Logout/', views.Logout, name='logout'),
]

