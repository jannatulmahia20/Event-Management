from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.db.models import Count, Q
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from .models import Event, Category
from .forms import CustomUserCreationForm
from .decorators import group_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

def dashboard(request):
    today = now().date()

    total_events = Event.objects.count()
    total_participants = User.objects.count()  
    upcoming_events = Event.objects.filter(date__gt=today).count()
    past_events = Event.objects.filter(date__lt=today).count()
    events_today = Event.objects.filter(date=today)

    context = {
        'total_events': total_events,
        'total_participants': total_participants,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'events_today': events_today,
    }

    return render(request, 'dashboard.html', context)


def event_list(request):
    query = request.GET.get('q')
    
    events = Event.objects.select_related('category').prefetch_related('participants')  # updated related_name

    if query:
        events = events.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    events = events.annotate(participant_count=Count('participants'))[:6]  # updated field name
    total_participants = User.objects.count()  # replaced Participant with User

    return render(request, 'event_list.html', {
        'events': events,
        'total_participants': total_participants,
        'query': query,  
    })


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


def event_detail(request, pk):
    event = get_object_or_404(Event.objects.prefetch_related('participants'), pk=pk)  
    return render(request, 'event_detail.html', {'event': event})


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  
            user.save()

            participant_group = Group.objects.get(name='Participant')
            user.groups.add(participant_group)

            return redirect('login')  
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@group_required('Admin')
def admin_dashboard(request):
    
    
    return render(request, 'admin_dashboard.html')

@group_required('Organizer')
def create_event(request):
    
    return render(request, 'create_event.html')

@group_required('Participant')
def participant_dashboard(request):
    
    return render(request, 'participant_dashboard.html')




@login_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user

    if user in event.rsvps.all():
        messages.info(request, "You have already RSVP'd for this event.")
    else:
        event.rsvps.add(user)
        messages.success(request, "Successfully RSVP'd!")

        send_mail(
            subject="RSVP Confirmation",
            message=f"Hi {user.first_name},\n\nYou've successfully RSVP'd for {event.name}.",
            from_email="noreply@example.com",
            recipient_list=[user.email],
            fail_silently=True,
        )

    return redirect('event_detail', pk=event.id)

