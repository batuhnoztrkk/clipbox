from django.urls import path
from . import views

app_name = 'panels'

urlpatterns = [
    path('', views.panel_list, name='list'),
    path('create/', views.panel_create, name='create'),
    path('detail/<int:pk>/', views.panel_detail, name='detail'),
    path('panel/edit/<int:id>/', views.panel_edit, name='edit'),
]