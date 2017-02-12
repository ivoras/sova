from django.db import models
from django.utils import timezone

class Person(models.Model):
    email = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

    def __str__(self):
        return "%s <%s>" % (self.name, self.email)

class Group(models.Model):
    name = models.CharField(max_length=100)
    persons = models.ManyToManyField(Person)
    email_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=100)
    header = models.TextField(default="Hi,")
    footer = models.TextField(default="----")
    date = models.DateTimeField()
    schedules = models.ManyToManyField(Group, through='EmailSchedule')

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
