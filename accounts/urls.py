from django.urls import path
from .views import register
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', views.login_view, name='login'),  # login adında url
]