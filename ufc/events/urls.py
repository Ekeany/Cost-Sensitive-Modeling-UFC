from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('future-event', views.future_event, name='future_event'),
    path('past-events', views.past_events_list, name='past_events_list'),
    path('past-event/<int:id>', views.past_event_details, name='past_events_detail')
]