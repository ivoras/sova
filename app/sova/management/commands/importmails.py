import csv
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.core.management import CommandError
from django.utils import timezone
from django.utils.html import strip_tags
from django.template.loader import get_template
from django.conf import settings
import logging

from sova.models import Person, Group, Event, EmailSchedule, GroupAutoParticipation, Participation

class Command(BaseCommand):
    help = 'Imports e-mails from CSV in the Google Groups format'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--csv', dest='csv', action='store', type=str)
        parser.add_argument('-g', '--group', dest='group', action='store', type=str, default='Hooligans')

    def handle(self, *args, **options):
        if len(options) < 1:
            raise CommandError("Expecting argument: -f filename")
        g = Group.objects.get(name=options['group'])
        filename = options['csv']
        for data in csv.reader(open(filename)):
            if len(data) < 3:
                continue
            if data[0].find('@') == -1:
                continue
            try:
                p = Person.objects.get(email=data[0])
            except Person.DoesNotExist:
                p = None
            if p is not None:
                continue
            p = Person(email=data[0], name=data[1], email_enabled=True)
            p.save()
            g.persons.add(p)
            print(p)