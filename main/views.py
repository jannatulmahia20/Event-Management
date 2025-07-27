from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.db.models import Count, Q
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import send_mail
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Event, Category
from .forms import CustomUserCreationForm, EventForm
from django.contrib.auth.decorators import login_required
from .decorators import group_required  
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy







class DashboardRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Admin').exists():
            return redirect('admin_dashboard')
        elif user.groups.filter(name='Organizer').exists():
            return redirect('organizer_dashboard')
        elif user.groups.filter(name='Participant').exists():
            return redirect('participant_dashboard')
        else:
            return redirect('login')





class EventListView(ListView):
    model = Event
    template_name = 'event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        query = self.request.GET.get('q')
        events = Event.objects.select_related('category').prefetch_related('rsvps')

        if query:
            events = events.filter(Q(name__icontains=query) | Q(location__icontains=query))
        
        return events.annotate(participant_count=Count('rsvps'))[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_participants'] = User.objects.count()
        context['query'] = self.request.GET.get('q', '')
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'




class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.prefetch_related('rsvps')


class SignupView(FormView):
    template_name = 'signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        participant_group = Group.objects.get(name='Participant')
        user.groups.add(participant_group)

        return super().form_valid(form) 



@group_required('Admin')

def admin_dashboard(request):

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



from django.utils.decorators import method_decorator

class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'create_event.html'
    success_url = '/events/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='Organizer').exists()

    @method_decorator(group_required('Organizer'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

