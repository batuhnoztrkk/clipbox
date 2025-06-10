from django.urls import path
from . import views

app_name = 'videos'

urlpatterns = [
    path('generate/<int:video_id>/', views.generate_video, name='generate_video'),
    path('', views.video_list, name='list'),
    path('create/', views.video_create, name='create'),
    path('<int:pk>/', views.video_detail, name='detail'),
    path('<int:pk>/edit/', views.video_edit, name='edit'),
]