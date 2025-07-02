from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('dashboard')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),  
    path('categories/', views.category_list, name='category_list'),
    
]
