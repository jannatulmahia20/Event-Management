from django.urls import path
from django.shortcuts import redirect
from .views import EventCreateView
from .views import SignupView

from django.contrib.auth import views as auth_views
from . import views
from .views import (
    DashboardRedirectView,
    EventListView,
    EventDetailView,
    EventCreateView,
    CategoryListView,
)

urlpatterns = [
    path('', lambda request: redirect('dashboard')),
    path('dashboard/', DashboardRedirectView.as_view(), name='dashboard'),

    # Auth
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Role-based dashboards (still FBVs)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('participant-dashboard/', views.participant_dashboard, name='participant_dashboard'),

    # Events (CBVs)
    path('events/', EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('create-event/', EventCreateView.as_view(), name='create_event'),
    path('categories/', CategoryListView.as_view(), name='category_list'),

    # RSVP (still FBV)
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
]
