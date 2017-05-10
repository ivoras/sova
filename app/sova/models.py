# -*- coding: utf-8 -*-
import bleach
from django.db import models
from django.utils import timezone
from tinymce.models import HTMLField


class Person(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    email_enabled = models.BooleanField(default=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    phone_enabled = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s <%s>" % (self.name, self.email)

    class Meta:
        ordering = ('name', )


class Group(models.Model):
    name = models.CharField(max_length=100)
    persons = models.ManyToManyField(Person)
    email_enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Event(models.Model):
    name = models.CharField(max_length=100)
    mail_prefix = models.CharField(max_length=100, blank=True, null=True)
    header = models.TextField(default="Hi,")
    footer = models.TextField(default="----")
    date = models.DateTimeField()
    deadline_for_joining = models.DateTimeField(null=True, blank=True)
    schedules = models.ManyToManyField(Group, through='EmailSchedule')
    participations = models.ManyToManyField(Person, through='Participation')

    def __unicode__(self):
        return u"%s %s" % (self.name, timezone.localtime(self.date).strftime('%d.%m.%Y. %H:%M'))


class EmailSchedule(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group)
    event = models.ForeignKey(Event)
    date = models.DateTimeField()
    subject = models.CharField(max_length=200)
    message = HTMLField()
    sent = models.BooleanField(default=False)
    add_custom_link_before_footer = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.message = bleach.clean(self.message)
        super(EmailSchedule, self).save(*args, **kwargs)

    def __unicode__(self):
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
    grade = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u"%s, %s: %s" % (self.person.name, self.event.name, u'✓' if self.participated else u'-')


class Token(models.Model):
    person = models.ForeignKey(Person)
    token = models.CharField(max_length=16)
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s, %s: %s" % (self.person.name, self.token, self.date_created)


