from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.db.models import Count
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Event, Category
from .forms import CustomUserCreationForm
from .decorators import group_required
from django.contrib import messages


@login_required
def dashboard(request):
    user = request.user
    if user.groups.filter(name='Admin').exists():
        return redirect('admin_dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer_dashboard')
    elif user.groups.filter(name='Participant').exists():
        return redirect('participant_dashboard')
    else:
        return redirect('login')


def event_list(request):
    query = request.GET.get('q')
    events = Event.objects.select_related('category').prefetch_related('rsvps')  # adjust if your m2m field is 'rsvps'

    if query:
        events = events.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    events = events.annotate(participant_count=Count('rsvps'))[:6]  # adjust field name if needed
    total_participants = User.objects.count()

    return render(request, 'event_list.html', {
        'events': events,
        'total_participants': total_participants,
        'query': query,
    })


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


def event_detail(request, pk):
    event = get_object_or_404(Event.objects.prefetch_related('rsvps'), pk=pk)
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

            # TODO: trigger activation email via signal

            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@group_required('Admin')
def admin_dashboard(request):
    # Add admin dashboard context if needed
    return render(request, 'admin_dashboard.html')


@group_required('Organizer')
def organizer_dashboard(request):
    user = request.user
    today = now().date()

    events = Event.objects.filter(created_by=user)
    total_events = events.count()
    total_participants = sum(event.rsvps.count() for event in events)  # adjust m2m name if needed
    upcoming_events = events.filter(date__gt=today).count()
    past_events = events.filter(date__lt=today).count()
    events_today = events.filter(date=today)

    context = {
        'total_events': total_events,
        'total_participants': total_participants,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'events_today': events_today,
    }
    return render(request, 'organizer_dashboard.html', context)


@group_required('Participant')
def participant_dashboard(request):
    user = request.user
    rsvp_events = user.rsvp_events.all()  # adjust related_name if different

    context = {
        'rsvp_events': rsvp_events,
    }
    return render(request, 'participant_dashboard.html', context)


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


from django.contrib.auth.decorators import login_required
from .decorators import group_required  

@group_required('Organizer')  
@login_required
def create_event(request):
   
    return render(request, 'create_event.html')
