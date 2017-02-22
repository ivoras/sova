import os
import base64


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.validators import validate_email
from django import forms
from django.utils import timezone
from django.conf import settings

from .models import Person, Event, Participation, Token


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


def vote(req, event, person):
    person = get_object_or_404(Person, pk=int(person))
    event = get_object_or_404(Event, pk=int(event))
    accepted = req.POST['choice']
    if not (accepted == 'True' or accepted == 'False'):
        # redisplay the form
        return render(req, 'sova/join.html', {
            'person': person,
            'event': event,
            'error_message': "You didn't select a choice.",
        })
    participation = Participation(person=person, event=event, accepted=accepted)
    participation.save()
    return HttpResponseRedirect(reverse('join', args=(person.pk, event.pk,)))


def accept(req, event, person):
    person = get_object_or_404(Person, pk=int(person))
    event = get_object_or_404(Event, pk=int(event))
    participation = Participation(person=person, event=event, accepted=True)
    participation.save()
    return HttpResponseRedirect(reverse('join', args=(person.pk, event.pk,)))


def get_profile_token(req, person=0):
    try:
        person = Person.objects.get(pk=int(person))
        token = Token.objects.filter(person=person.id, date_created__gte=timezone.now() - timezone.timedelta(minutes=settings.TOKEN_EXPIRY_TIME)).order_by('-id')[0]
    except Person.DoesNotExist:
        person = None
        token = None
    except Token.DoesNotExist:
        token = None
    return render(req, 'sova/getprofiletoken.html', {
            'person': person,
            'token' : token,
    })


def send_profile_token(req):
    profile = req.POST.get('profile_email', False)
    # no email address meaning just show the form
    if not profile:
        return HttpResponseRedirect(reverse('getprofiletoken'))
    # otherwise, validate it and retrieve the Person
    try:
        validate_email(profile)
        person = get_object_or_404(Person, email=str(profile))
        token = Token(token=base64.urlsafe_b64encode(os.urandom(12)), person=person)
        token.save()
        return HttpResponseRedirect(reverse('getprofiletoken', args=(person.id,)))
    except forms.ValidationError:
        return render(req, 'sova/getprofiletoken.html', {
            'error_message': "You've entered an invalid e-mail address",
     })


def edit_user_profile(req, token=''):
    try:
        token = Token.objects.filter(token=token, date_created__gte=timezone.now() - timezone.timedelta(minutes=settings.TOKEN_EXPIRY_TIME)).order_by('-id')
        if (token):
            token = token[0]
    # either no token or token has expired
    except Token.DoesNotExist:
        token = None
    return render(req, 'sova/edituserprofile.html', {
            'token': token,
    })

def save_user_profile(req, token=''):
    return HttpResponseRedirect(reverse('edituserprofile'), args=(token.id,))

