from django.urls import path
from . import views

app_name = 'videos'

urlpatterns = [
    path('<int:video_id>/generate/<str:step>/', views.generate_content, name='generate_content'),
    path('', views.video_list, name='list'),
    path('create/<int:panel_id>/', views.video_create, name='create'),
    path('<int:pk>/', views.video_detail, name='detail'),
    path('<int:pk>/edit/', views.video_edit, name='edit'),
]