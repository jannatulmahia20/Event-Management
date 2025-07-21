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
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

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


from django.contrib.sites.shortcuts import get_current_site

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # deactivate until email confirmed
            user.save()

            participant_group = Group.objects.get(name='Participant')
            user.groups.add(participant_group)

            # Send activation email
            send_activation_email(request, user)

            messages.success(request, 'Please confirm your email to complete registration.')
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
@login_required
def participant_dashboard(request):
    user = request.user
    rsvped_events = user.rsvped_events.all()  
    return render(request, 'participant_dashboard.html', {
        'rsvped_events': rsvped_events,
    })

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


from django.contrib.auth import get_user_model

def send_activation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    message = render_to_string('activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = "html"
    email.send()

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, '✅ Your account has been activated successfully! You can now log in.')
        else:
            messages.info(request, ' Your account is already activated.')
        return redirect('login')
    else:
        messages.error(request, '❌ Activation link is invalid or expired.')
        return render(request, 'activation_invalid.html')


from .forms import EventForm

def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('event_list')  # Redirect after successful event creation
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})
