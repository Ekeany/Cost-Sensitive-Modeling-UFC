from django.shortcuts import render, get_object_or_404
from .models import Event

# Create your views here.

# View to display the upcoming event
def future_event(request):
    futureEvent = Event.objects.is_next()
    return render(request,
                'future_event.html',
                {'futureEvent': futureEvent})

# View to display the list of past events
def past_events_list(request):
    pastEvent = Event.objects.is_past()
    return render(request,
                'past_events_list.html',
                {'pastEvent': pastEvent})

# View to display the past event by id
def past_event_details(request, id):
    pastEvent = Event.objects.is_past()
    pastEvent = get_object_or_404(Event,
                                id=id)
    return render(request,
                'past_event_details.html',
                {'event': pastEvent})