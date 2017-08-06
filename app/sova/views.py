import base64
#from datetime import datetime
import os

from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.validators import validate_email
from django import forms
from django.utils import timezone
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib import messages
from django.template.loader import get_template

from .models import Person, Event, Participation, EmailSchedule, Token


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


def accept(req, schedule, person):
    """
    Shows event info and allows the user to accept.
    """
    schedule = get_object_or_404(EmailSchedule, pk=int(schedule))
    person = get_object_or_404(Person, pk=int(person))
    people_count = Participation.objects.filter(event=schedule.event, accepted=True).count()
    if schedule.event.max_people and people_count >= schedule.event.max_people:
        return render(req, 'sova/noroom.html', { 'person': person, 'schedule': schedule })
    if timezone.now() > schedule.event.date or (schedule.event.deadline_for_joining and timezone.now() > schedule.event.deadline_for_joining):
        return render(req, 'sova/toolate.html', { 'person': person, 'schedule': schedule })

    people_percent = int((people_count / schedule.event.max_people) * 100) if schedule.event.max_people else 0

    try:
        participation = Participation.objects.get(person=person, event=schedule.event)
        if participation.accepted:
            return render(req, 'sova/unaccept.html', { 'person': person, 'schedule': schedule, 'people_count': people_count, 'people_percent': people_percent })
    except Participation.DoesNotExist:
        pass

    return render(req, 'sova/accept.html', { 'person': person, 'schedule': schedule, 'people_count': people_count, 'people_percent': people_percent })


def confirm(req, schedule, person):
    """
    Notifies the user he/she has confirmed attendance.
    """
    schedule = get_object_or_404(EmailSchedule, pk=int(schedule))
    person = get_object_or_404(Person, pk=int(person))

    try:
        participation = Participation.objects.get(person=person, event=schedule.event)
        participation.accepted = True
    except Participation.DoesNotExist:
        participation = Participation(person=person, event=schedule.event, accepted=True)
    participation.save()

    tpl = get_template('sova/confirmemail.html')
    html = tpl.render({ 'person': person, 'schedule': schedule, 'participation': participation, 'email_admin': settings.EMAIL_ADMIN })
    subject = "[%s] %s - potvrda!" % (schedule.event.mail_prefix, schedule.name)
    plain_text = strip_tags(html)

    msg = EmailMultiAlternatives(subject, plain_text, settings.EMAIL_FROM, [person.email])
    msg.attach_alternative(html, "text/html")
    msg.send()

    return render(req, 'sova/confirm.html', { 'person': person, 'schedule': schedule, 'participation': participation })


def unaccept(req, schedule, person):
    """
    Notifies the user he/she has canceled attendance.
    """
    schedule = get_object_or_404(EmailSchedule, pk=int(schedule))
    person = get_object_or_404(Person, pk=int(person))

    try:
        participation = Participation.objects.get(person=person, event=schedule.event)
        participation.accepted = False
    except Participation.DoesNotExist:
        participation = Participation(person=person, event=schedule.event, accepted=False)
    participation.save()

    tpl = get_template('sova/unacceptemail.html')
    html = tpl.render({ 'person': person, 'schedule': schedule, 'participation': participation, 'email_admin': settings.EMAIL_ADMIN })
    subject = "[%s] %s - otkazivanje" % (schedule.event.mail_prefix, schedule.name)
    plain_text = strip_tags(html)

    msg = EmailMultiAlternatives(subject, plain_text, settings.EMAIL_FROM, [person.email])
    msg.attach_alternative(html, "text/html")
    msg.send()

    return render(req, 'sova/unacceptconfirm.html', { 'person': person, 'schedule': schedule, 'participation': participation })


def exitpoll(req, schedule, person):
    """
    Shows event exit poll.
    """
    schedule = get_object_or_404(EmailSchedule, pk=int(schedule))
    person = get_object_or_404(Person, pk=int(person))
    people_count = Participation.objects.filter(event=schedule.event, accepted=True, participated=True).count()
    people_percent = int((people_count / schedule.event.max_people) * 100) if schedule.event.max_people else 0
    participation = get_object_or_404(Participation, person=person, event=schedule.event)
    return render(req, 'sova/exitpoll.html', { 'person': person, 'schedule': schedule, 'people_count': people_count, 'people_percent': people_percent })

def exitpollsave(req, schedule, person):
    """
    Saves the exit poll results.
    """
    schedule = get_object_or_404(EmailSchedule, pk=int(schedule))
    person = get_object_or_404(Person, pk=int(person))
    participation = get_object_or_404(Participation, person=person, event=schedule.event)

    participation.poll_grade = int(req.POST['grade'])
    participation.poll_best = req.POST['best']
    participation.poll_worst = req.POST['worst']
    participation.poll_futureorg = True if 'futureorg' in req.POST and req.POST['futureorg'] == '1' else False
    participation.poll_change = req.POST['change']
    participadion.save()

    return render(req, 'sova/exitpollthanks.html', { 'person': person, 'schedule': schedule })
    
def contact(req):
    return render(req, 'sova/contact.html', {})

def get_profile_token(req, person=0):
    try:
        person = Person.objects.get(pk=int(person))
        token = Token.objects.filter(person=person.id, date_created__gte=timezone.now() - timezone.timedelta(
            minutes=settings.TOKEN_EXPIRY_TIME)).order_by('-id')[0]
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
    # otherwise, validate it and retrieve the Person
    try:
        validate_email(profile)
        person = get_object_or_404(Person, email=str(profile))
        token = Token(token=base64.urlsafe_b64encode(os.urandom(12)), person=person)
        token.save()
        # send email, something along these lines
        # subject, from_email, to = 'Token', settings.EMAIL_FROM, person.email
        # text_content = 'Your token is ' + token.token
        # html_content = '<a href="{% url edituserprofile token.token %} ">'
        # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        # msg.attach_alternative(html_content, "text/html")
        # msg.send()
        return HttpResponseRedirect(reverse('getprofiletoken', args=(person.id,)))
    except forms.ValidationError:
        messages.error(req, "You've entered an invalid e-mail address")
        return render(req, 'sova/getprofiletoken.html')


def edit_user_profile(req, token=''):
    try:
        token = Token.objects.get(token=token, date_created__gte=timezone.now() - timezone.timedelta(
            minutes=settings.TOKEN_EXPIRY_TIME))
    # either no token or token has expired
    except Token.DoesNotExist:
        token = None
    return render(req, 'sova/edituserprofile.html', {
            'token': token,
    })


def save_user_profile(req, token=''):
    try:
        retrieved_token = Token.objects.get(token=token, date_created__gte=timezone.now() - timezone.timedelta(
            minutes=settings.TOKEN_EXPIRY_TIME))
        retrieved_token.person.name = req.POST.get('username', retrieved_token.person.name)
        if req.POST.get('email_enabled', False):
            retrieved_token.person.email_enabled = True
        else:
            retrieved_token.person.email_enabled = False
        retrieved_token.person.phone = req.POST.get('phone', retrieved_token.person.phone)
        if req.POST.get('phone_enabled', False):
            retrieved_token.person.phone_enabled = True
        else:
            retrieved_token.person.phone_enabled = False
        retrieved_token.person.save()
        messages.success(req, 'Successfull edit')
    except Token.DoesNotExist:
        token = None
        messages.error(req, 'Token expired :(')
        return render(req, 'sova/edituserprofile.html', {
            'token': token,
        })
    except forms.ValidationError:
        messages.error(req, 'Form validation problem :(')
        return render(req, 'sova/edituserprofile.html', {
            'token': token,
        })

    return HttpResponseRedirect(reverse('edituserprofile', args=(retrieved_token.token,)))

