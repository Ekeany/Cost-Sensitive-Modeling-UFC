from django.shortcuts import render, get_object_or_404
from .models import Event
from .models import Fight

# Create your views here.

# View to display the upcoming event
def future_event(request):
    futureEvent = Event.objects.is_next()
    for event in futureEvent:
        eventFights = event.fights.all()
    return render(request,
                'future_event.html',
                {'futureEvent': futureEvent,
                 'eventFights': eventFights})

# View to display the list of past events
def past_events_list(request):
    pastEvent = Event.objects.is_past()
    return render(request,
                'past_events_list.html',
                {'pastEvent': pastEvent})

# View to display the past event by id
def past_event_details(request, id):
    pastEvent = get_object_or_404(Event, id=id)
    eventFights = pastEvent.fights.all()
    return render(request,
                'past_event_details.html',
                {'pastEvent': pastEvent,
                 'eventFights': eventFights})