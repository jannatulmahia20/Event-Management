from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import create_event



urlpatterns = [
    path('', lambda request: redirect('dashboard')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),  
    path('categories/', views.category_list, name='category_list'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-event/', views.create_event, name='create_event'),
    path('participant-dashboard/', views.participant_dashboard, name='participant_dashboard'),
    
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('create-event/', create_event, name='create_event'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



    

