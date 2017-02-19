from django.shortcuts import render
from .models import Person, Event


def index(req):
    return render(req, 'sova/index.html')


def join(req, event, person):
    person = Person.objects.get(pk=int(person))
    event = Event.objects.get(pk=int(event))
    context = {
        'person': person,
        'event': event
    }
    return render(req, 'sova/join.html', context)
