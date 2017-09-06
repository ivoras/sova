from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.html import strip_tags
from django.template.loader import get_template
from django.conf import settings
import logging

from sova.models import Person, Group, Event, EmailSchedule, GroupAutoParticipation, Participation

class Command(BaseCommand):
    help = 'Sends e-mails'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for es in EmailSchedule.objects.select_related().filter(date__lte=timezone.now(), sent=False):
            if not es.group.email_enabled:
                continue
            self.stdout.write("%s Scheduled to send: %s" % (datetime.now().isoformat(), str(es)))
            if es.event.mail_prefix:
                subject = "[%s] %s" % (es.event.mail_prefix, es.name)
            else:
                subject = es.name
            auto_accepted_ids = set()
            if es.target == EmailSchedule.SEND_EVERYONE:
                recipients = es.group.persons.filter(email_enabled=True)
                template_file = 'sova/acceptemail.html'
                if es.type == EmailSchedule.TYPE_INVITATION:
                    auto_participation_recipients = recipients & Person.objects.filter(groupautoparticipation__group=es.group)
                    for r in auto_participation_recipients:
                        if Participation.objects.filter(event=es.event, person=r).count() == 0:
                            p = Participation(event=es.event, person=r, accepted=True)
                            p.save()
                        auto_accepted_ids.add(r.id)
            elif es.target == EmailSchedule.SEND_ACCEPTED:
                recipients = es.group.persons.filter(email_enabled=True) & Person.objects.filter(participation__event=es.event, participation__accepted=True)
                template_file = 'sova/acceptemail.html'
            elif es.target == EmailSchedule.SEND_NOT_ACCEPTED:
                recipients = set(es.group.persons.filter(email_enabled=True)) - set(Person.objects.filter(participation__event=es.event, participation__accepted=True))
                template_file = 'sova/acceptemail.html'
            elif es.target == EmailSchedule.SEND_YES_REQUIREMENTS:
                recipients = es.group.persons.filter(email_enabled=True) & Person.objects.filter(participation__event=es.event, participation__requirements_done=True)
                template_file = 'sova/acceptemail.html'
            elif es.target == EmailSchedule.SEND_NO_REQUIREMENTS:
                recipients = es.group.persons.filter(email_enabled=True) & Person.objects.filter(participation__event=es.event, participation__requirements_done=False)
                template_file = 'sova/acceptemail.html'
            elif es.target == EmailSchedule.SEND_PARTICIPATED and es.type == EmailSchedule.TYPE_EXIT_POLL:
                recipients = es.group.persons.filter(email_enabled=True) & Person.objects.filter(participation__event=es.event, participation__participated=True)
                template_file = 'sova/exitpollemail.html'
            else:
                self.stdout.write("Unknown schedule target: %s" % es.target)
                
            for recipient in recipients:
                plain_text = "%s\n\n%s\n\n%s\n" % (strip_tags(es.event.header), strip_tags(es.message), strip_tags(es.event.footer))
                html = get_template(template_file)
                context = {
                    'person': recipient,
                    'schedule': es,
                    'server':  settings.SOVA_BASE_URL,
                }
                if es.type == EmailSchedule.TYPE_INVITATION:
                    context['auto_accepted'] = recipient.id in auto_accepted_ids
                html_content = html.render(context)
                msg = EmailMultiAlternatives(subject, plain_text, settings.EMAIL_FROM, [recipient.email])
                msg.extra_headers['Reply-To'] = settings.EMAIL_REPLY_TO
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                self.stdout.write("Sent '%s' to '%s'" % (subject, recipient.email))
            es.sent = True
            es.save()
