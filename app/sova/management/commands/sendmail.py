from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
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
            if es.target == EmailSchedule.SEND_EVERYONE:
                recipients = es.group.persons.filter(email_enabled=True)
            elif es.target == EmailSchedule.SEND_ACCEPTED:
                recipients = es.group.persons.filter(email_enabled=True)

            for recipient in recipients:
                plain_text = "%s\n\n%s\n\n%s\n" % (strip_tags(es.event.header), strip_tags(es.message), strip_tags(es.event.footer))
                html = get_template('sova/acceptemail.html')
                context = {
                    'person': recipient,
                    'schedule': es,
                    'server':  settings.SOVA_BASE_URL,
                }
                html_content = html.render(context)
                msg = EmailMultiAlternatives(subject, plain_text, settings.EMAIL_FROM, [recipient.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            es.sent = True
            es.save()
