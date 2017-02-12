from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from sova.models import Person, Group, Event, EmailSchedule

class Command(BaseCommand):
    help = 'Sends e-mails'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for es in EmailSchedule.objects.select_related().filter(date__lte=timezone.now(), sent = False):
            self.stdout.write("Scheduled to send: " + str(es))
            if es.event.mail_prefix:
                subject = "[%s] %s" % (es.event.mail_prefix, es.name)
            else:
                subject = es.name
            recipients = [ p.email for p in es.group.persons.all() ]
            send_mail(subject, "%s\n\n%s\n\n%s\n" % (es.event.header, es.message, es.event.footer), 'Hoo <donotreply@fielder.ivoras.net>', recipients)
            es.sent = True
            es.save()
