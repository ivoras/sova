from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.loader import get_template
from django.conf import settings

from sova.models import Person, Group, Event, EmailSchedule

class Command(BaseCommand):
    help = 'Sends e-mails'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for es in EmailSchedule.objects.select_related().filter(date__lte=timezone.now(), sent=False):
            if not es.group.email_enabled:
                continue
            self.stdout.write("Scheduled to send: " + str(es))
            if es.event.mail_prefix:
                subject = "[%s] %s" % (es.event.mail_prefix, es.name)
            else:
                subject = es.name
            for recipient in es.group.persons.filter(email_enabled=True):
                plain_text = "%s\n\n%s\n\n%s\n" % (es.event.header, es.message, es.event.footer)
                html = get_template('sova/confirmationemail.html')
                protocol = 'http://' # get this from settings?
                port = ':8000' # get this from settings?
                context = {
                    'person': recipient,
                    'schedule': es,
                    'server':  protocol + settings.ALLOWED_HOSTS[1] + port,  # there has to be a better way to do this
                }
                html_content = html.render(context)
                msg = EmailMultiAlternatives(subject, plain_text, 'Hoo <donotreply@fielder.ivoras.net>', [recipient.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            es.sent = True
            es.save()
