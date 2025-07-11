from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Count
from .models import Event, Participant
from django.db.models import Q

def dashboard(request):
    today = now().date()

    total_events = Event.objects.count()
    total_participants = Participant.objects.count()
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
    
    events = Event.objects.select_related('category').prefetch_related('participant_set')

    if query:
        events = events.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    events = events.annotate(participant_count=Count('participant'))[:6]
    total_participants = Participant.objects.count()

    return render(request, 'event_list.html', {
        'events': events,
        'total_participants': total_participants,
        'query': query,  
    })
from .models import Category

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

from django.shortcuts import get_object_or_404

def event_detail(request, pk):
    event = get_object_or_404(Event.objects.prefetch_related('participant_set'), pk=pk)
    return render(request, 'event_detail.html', {'event': event})



