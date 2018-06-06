# -*- coding: utf-8 -*-
from .util import bleach_htmlfield
from django.db import models
from django.utils import timezone
import random
from tinymce.models import HTMLField


def random_p_pkey():
    random.seed()
    while True:
        n = random.randrange(0xfffffff)
        try:
            p = Person.objects.get(id=n)
        except Person.DoesNotExist:
            return n

def random_es_pkey():
    random.seed()
    while True:
        n = random.randrange(0xfffffff)
        try:
            es = EmailSchedule.objects.get(id=n)
        except EmailSchedule.DoesNotExist:
            return n


class Person(models.Model):
    id = models.IntegerField(primary_key=True, default=random_p_pkey)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    email_enabled = models.BooleanField(default=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    phone_enabled = models.BooleanField(default=False)
    time_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return u"%s <%s>" % (self.name, self.email)

    class Meta:
        ordering = ('name', )


class Group(models.Model):
    name = models.CharField(max_length=100)
    persons = models.ManyToManyField(Person)
    email_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )

class Event(models.Model):
    name = models.CharField(max_length=100)
    hype_text = models.TextField()
    mail_prefix = models.SlugField(max_length=100, blank=True, null=True)
    organiser = models.ForeignKey(Person, related_name='event_organiser')
    header = HTMLField(default="Hi,\nTko ne dođe na ovu hoo, smrdi!")
    footer = HTMLField(default="----")
    date = models.DateTimeField(verbose_name="Date of event")
    deadline_for_joining = models.DateTimeField(null=True, blank=True)
    schedules = models.ManyToManyField(Group, through='EmailSchedule')
    participations = models.ManyToManyField(Person, through='Participation')
    max_people = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return u"%s %s" % (self.name, timezone.localtime(self.date).strftime('%d.%m.%Y. %H:%M'))

    class Meta:
        ordering = ('-date', )


class EventOption(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Event)

    def __str__(self):
        return self.name

class EmailSchedule(models.Model):
    SEND_EVERYONE = 1
    SEND_ACCEPTED = 2
    SEND_NOT_ACCEPTED = 3
    SEND_NO_REQUIREMENTS = 4
    SEND_YES_REQUIREMENTS = 5
    SEND_PARTICIPATED = 6
    SEND_CHOICES = (
        (SEND_EVERYONE, "Svima u grupi"),
        (SEND_ACCEPTED, "Onima koji su prihvatili"),
        (SEND_NOT_ACCEPTED, "Onima koji nisu prihvatili"),
        (SEND_NO_REQUIREMENTS, "Onima koji nemaju preduvjete"),
        (SEND_YES_REQUIREMENTS, "Onima koji imaju preduvjete"),
        (SEND_PARTICIPATED, "Onima koji su sudjelovali"),
    )

    TYPE_MESSAGE = 1
    TYPE_INVITATION = 2
    TYPE_EXIT_POLL = 3
    TYPE_CHOICES = (
        (TYPE_MESSAGE, "Obavijest"),
        (TYPE_INVITATION, "Pozivnica"),
        (TYPE_EXIT_POLL, "Anketa nakon događaja")
    )

    id = models.IntegerField(primary_key=True, default=random_es_pkey)
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group)
    target = models.IntegerField(choices=SEND_CHOICES, default=SEND_EVERYONE)
    event = models.ForeignKey(Event)
    type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_MESSAGE)
    date = models.DateTimeField(db_index=True)
    subject = models.CharField(max_length=200)
    message = HTMLField()
    sent = models.BooleanField(default=False)
    add_custom_link_before_footer = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.message = bleach_htmlfield(self.message)
        super(EmailSchedule, self).save(*args, **kwargs)

    def __str__(self):
        return u"%s (%s) @ %s" % (self.name, str(self.event), timezone.localtime(self.date).strftime('%d.%m.%Y. %H:%M'))

    class Meta:
        ordering = ('-date', )


class Participation(models.Model):
    date_entered = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event)
    person = models.ForeignKey(Person)
    requirements_done = models.BooleanField(default=False) # Participation requirements (e.g. payment) have been satisfied
    participated = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False) # They probably won't open the link if they don't want to participate, but we still need to track OR change this into an autoaccept link
    options = models.ManyToManyField(EventOption, blank=True)

    poll_grade = models.IntegerField(blank=True, null=True)
    poll_best = models.TextField(blank=True, null=True)
    poll_worst = models.TextField(blank=True, null=True)
    poll_change = models.TextField(blank=True, null=True)
    poll_futureorg = models.BooleanField(default=False)
    poll_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return u"%s, %s: %s" % (self.person.name, self.event.name, u'✓' if self.participated else u'-')


class GroupAutoParticipation(models.Model):
    group = models.ForeignKey(Group)
    person = models.ForeignKey(Person)

    def __str__(self):
        return "%s: %s" % (self.group.name, self.person.name)

class Token(models.Model):
    person = models.ForeignKey(Person)
    token = models.CharField(max_length=16)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u"%s, %s: %s" % (self.person.name, self.token, self.date_created)

