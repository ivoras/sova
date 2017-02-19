# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

class Person(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    email_enabled = models.BooleanField(default=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    phone_enabled = models.BooleanField(default=False)

    def __str__(self):
        return "%s <%s>" % (self.name, self.email)

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
    mail_prefix = models.CharField(max_length=100, blank=True, null=True)
    header = models.TextField(default="Hi,")
    footer = models.TextField(default="----")
    date = models.DateTimeField()
    schedules = models.ManyToManyField(Group, through='EmailSchedule')
    participations = models.ManyToManyField(Person, through='Participation')

    def __str__(self):
        return "%s %s" % (self.name, timezone.localtime(self.date).strftime('%d.%m.%Y. %H:%M'))


class EmailSchedule(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group)
    event = models.ForeignKey(Event)
    date = models.DateTimeField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return "%s (%s) @ %s" % (self.name, str(self.event), timezone.localtime(self.date).strftime('%d.%m.%Y. %H:%M'))

    class Meta:
        ordering = ('-date', )

class Participation(models.Model):
    date_entered = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event)
    person = models.ForeignKey(Person)
    requirements_done = models.BooleanField(default=False)
    participated = models.BooleanField(default=False)
    grade = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s, %s: %s" % (self.person.name, self.event.name, '✓' if self.participated else '-')

