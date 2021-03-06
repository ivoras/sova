import base64
from datetime import datetime, timedelta
import re
import os

from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.urls import reverse
from django.core.validators import validate_email
from django import forms
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib import messages
from django.template.loader import get_template
from django.contrib.auth import authenticate, login, logout

from .models import Person, Group, Event, Participation, EmailSchedule, Token, EventOption


RE_EMAIL = re.compile(r'^[^@]+@[^@]+\.[^@.]+')
TS_FORMAT = '%Y-%m-%dT%H:%M'

def index(req):
    if not req.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    organiser = Person.objects.get(email=req.user.email)
    ctx = { 'events': [ {'id': e.id, 'name': e.name, 'date': e.date} for e in Event.objects.filter(organiser=organiser).order_by('-date')] }
    return render(req, 'sova/index.html', ctx)

def vlogin(req):
    ctx = {}
    if req.method == 'GET':
        return render(req, 'sova/login.html', ctx)
    user = authenticate(username=req.POST['username'], password=req.POST['password'])
    if user == None:
        ctx['error'] = 'Invalid login'
        return render(req, 'sova/login.html', ctx)
    if not user.is_staff:
        ctx['error'] = 'Access denied'
        return render(req, 'sova/login.html', ctx)
    login(req, user)
    return HttpResponseRedirect(reverse('index'))

def vlogout(req):
    logout(req)
    return HttpResponseRedirect(reverse('index'))

def about(req):
    ctx = {}
    return render(req, 'sova/about.html', ctx)

def newevent(req):
    if not (req.user.is_authenticated and req.user.is_staff):
        return HttpResponseRedirect(reverse('index'))
    organiser = Person.objects.get(email=req.user.email)
    if req.method == 'GET':
        now = datetime.now()
        ctx = {'groups': [ {"id": g.id, "name": g.name } for g in Group.objects.order_by('name') ], 'eventDate': (now + timedelta(days=7)).strftime(TS_FORMAT), 'invitationDate': (now + timedelta(days=3)).strftime(TS_FORMAT), 'acceptDate': (now + timedelta(days=6, hours=12)).strftime(TS_FORMAT), 'reminderDate': (now + timedelta(days=5)).strftime(TS_FORMAT),'detailsDate': (now + timedelta(days=6)).strftime(TS_FORMAT), 'thanksDate': (now + timedelta(days=8)).strftime(TS_FORMAT)}
        return render(req, 'sova/newevent.html', ctx)
    
    dateEvent = datetime.strptime(req.POST['dateEvent'], TS_FORMAT)
    dateAccept = datetime.strptime(req.POST['dateAccept'], TS_FORMAT)
    maxPeople = int(req.POST['maxPeople']) if req.POST['maxPeople'] != '' else None
    group = Group.objects.get(id=int(req.POST['group']))

    e = Event(name=req.POST['name'], hype_text=req.POST['hypeText'], mail_prefix=req.POST['slug'], organiser=organiser, header=mark_safe(req.POST['header']), footer=mark_safe(req.POST['footer']), date=dateEvent, deadline_for_joining=dateAccept,
    max_people=maxPeople)
    e.save()

    invitationDate = datetime.strptime(req.POST['invitationDate'], TS_FORMAT)
    invitationES = EmailSchedule(name='Pozivnica: %s' % e.name,
    group=group, target=EmailSchedule.SEND_EVERYONE, event=e, type=EmailSchedule.TYPE_INVITATION, date=invitationDate, subject='Pozivnica: %s' % e.name, message=mark_safe(req.POST['invitationText']))
    invitationES.save()

    reminderDate = datetime.strptime(req.POST['reminderDate'], TS_FORMAT)
    reminderES = EmailSchedule(name='Pozivnica: %s (podsjetnik)' % e.name, group=group, target=EmailSchedule.SEND_NOT_ACCEPTED, event=e, type=EmailSchedule.TYPE_INVITATION, date=reminderDate, subject='Pozivnica: %s (podsjetnik)' % e.name, message=mark_safe(req.POST['invitationText']))
    reminderES.save()

    detailsDate = datetime.strptime(req.POST['detailsDate'], TS_FORMAT)
    detailsES = EmailSchedule(name='Detalji: %s' % e.name, group=group, target=EmailSchedule.SEND_ACCEPTED, event=e, type=EmailSchedule.TYPE_MESSAGE, date=detailsDate, subject='%s' % e.name, message=mark_safe(req.POST['detailsText']))
    detailsES.save()

    thanksDate = datetime.strptime(req.POST['thanksDate'], TS_FORMAT)
    thanksES = EmailSchedule(name='Zahvalnica: %s' % e.name, group=group, target=EmailSchedule.SEND_ACCEPTED, event=e, type=EmailSchedule.TYPE_EXIT_POLL, date=thanksDate, subject='Zahvalnica: %s' % e.name, message=mark_safe(req.POST['thanksText']))
    thanksES.save()

    return HttpResponseRedirect(reverse('index'))


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
    people_percent = int((people_count / schedule.event.max_people) * 100) if schedule.event.max_people else 0

    try:
        participation = Participation.objects.get(person=person, event=schedule.event)

        if participation.accepted:
            return render(req, 'sova/unaccept.html', { 'person': person, 'schedule': schedule, 'people_count': people_count, 'people_percent': people_percent })
        options = EventOption.objects.filter(event_id = schedule.event_id)
    except Participation.DoesNotExist:
        options = []

    if schedule.event.max_people and people_count >= schedule.event.max_people:
        return render(req, 'sova/noroom.html', { 'person': person, 'schedule': schedule })
    if timezone.now() > schedule.event.date or (schedule.event.deadline_for_joining and timezone.now() > schedule.event.deadline_for_joining):
        return render(req, 'sova/toolate.html', { 'person': person, 'schedule': schedule })

    return render(req, 'sova/accept.html', { 'person': person, 'schedule': schedule, 'people_count': people_count, 'people_percent': people_percent, 'options': options })


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
    return render(req, 'sova/exitpoll.html', { 'person': person, 'schedule': schedule, 'people_count': people_count, 'people_percent': people_percent, 'participation': participation })

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
    participation.poll_note = req.POST['note']
    participation.save()

    return render(req, 'sova/exitpollthanks.html', { 'person': person, 'schedule': schedule })

def unsubscribe(req, person):
    """
    Shows the unsubscribe form to the user.
    """
    person = get_object_or_404(Person, pk=int(person))
    return render(req, 'sova/unsubscribe.html', { 'person': person })

def unsubscribesave(req, person):
    if req.POST['unsubscribe'] == '1':
        person = get_object_or_404(Person, pk=int(person))
        person.email_enabled = False
        person.save()
        return render(req, 'sova/unsubscribe_yes.html', { 'person': person })
    else:
        return render(req, 'sova/unsubscribe_no.html', { 'person': person })

def subscribe(req):
    if settings.SUBSCRIBE_ENABLED:
        return render(req, 'sova/subscribe.html', { 'org_title': settings.ORG_TITLE, 'cfg': settings.CFG })
    else:
        raise Http404("Subscribing not enabled")

def subscribesave(req):
    if not settings.SUBSCRIBE_ENABLED:
        raise Http404("Subscribing not enabled")
    m = RE_EMAIL.match(req.POST['email'])
    if m == None:
        return subscribe(req)
    """
    When your users submit the form where you integrated reCAPTCHA, you'll get as part of the payload a string with the name "g-recaptcha-response". In order to check whether Google has verified that user, send a POST request with these parameters:
URL: https://www.google.com/recaptcha/api/siteverify
secret (required)	6LdfeFsUAAAAAIJpr3bug3TF3BQzNGN_MIAQ1QR5
response (required)	The value of 'g-recaptcha-response'.
remoteip	The end user's ip address.
The reCAPTCHA documentation site describes more details and advanced configurations.
    """



def subscribeconfirm(req):
    if not settings.SUBSCRIBE_ENABLED:
        raise Http404("Subscribing not enabled")

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

