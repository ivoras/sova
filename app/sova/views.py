from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Person, Event, Participation


def index(req):
    return render(req, 'sova/index.html')


def join(req, event, person):
    person = get_object_or_404(Person, pk=int(person))
    event = get_object_or_404(Event, pk=int(event))
    try:
        participation = Participation.objects.get(person=person, event=event)
    except Participation.DoesNotExist:
        participation = None
    context = {
        'person': person,
        'event': event,
        'participation': participation
    }
    return render(req, 'sova/join.html', context)


def vote(request, event, person):
    person = get_object_or_404(Person, pk=int(person))
    event = get_object_or_404(Event, pk=int(event))
    accepted = request.POST['choice']
    if not (accepted == 'True' or accepted == 'False'):
        # redisplay the form
        return render(request, 'sova/join.html', {
            'person': person,
            'event': event,
            'error_message': "You didn't select a choice.",
        })
    participation = Participation(person=person, event=event, accepted=accepted)
    participation.save()
    return HttpResponseRedirect(reverse('join', args=(person.pk, event.pk,)))
