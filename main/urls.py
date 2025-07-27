from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', lambda request: redirect('dashboard')),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('participant-dashboard/', views.participant_dashboard, name='participant_dashboard'),

    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('create-event/', views.create_event, name='create_event'),
    path('categories/', views.category_list, name='category_list'),
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
]
