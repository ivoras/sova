from django.contrib import admin

from .models import Person, Group, Event, EmailSchedule, Participation, GroupAutoParticipation, Token

class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'email_enabled', 'phone_enabled')
    search_fields = ('name', 'email')
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ("Kontakt e-mail", {
            'fields': ('email', 'email_enabled')
        }),
        ("Kontakt telefon", {
            'fields': ('phone', 'phone_enabled')
        })
    )

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_enabled')
    search_fields = ('name', )

class EmailScheduleInline(admin.StackedInline):
    model = EmailSchedule

class ParticipationInline(admin.StackedInline):
    model = Participation

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'mail_prefix', 'date')
    search_fields = ('name',)
    inlines = ( EmailScheduleInline, ParticipationInline )
    prepopulated_fields = { 'mail_prefix': ('name',) }

class EmailScheduleAdmin(admin.ModelAdmin):
    list_display = ('date', 'event', 'name', 'subject', 'type', 'group', 'target', 'sent')
    list_filter = ('event__name', 'date', 'sent', 'group', 'type', 'target')
    search_fields = ('name', 'group__name', 'event__name', 'target')
    fieldsets = (
        (None, {
            'fields': ('name', 'event')
        }),
        ("Datum slanja maila", {
            'fields': ('date',)
        }),
        ("Ciljana publika", {
            'fields': ('group', 'target', 'type')
        }),
        ("Poruka za slanje", {
            'fields': ('subject', 'message')
        }),
        ("Debug", {
            'fields': ('sent',)
        })
    )

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('person', 'event', 'poll_grade', 'participated')
    list_filter = ('person', 'event', 'poll_grade', 'participated')

class GroupAutoParticipationAdmin(admin.ModelAdmin):
    list_display = ('group', 'person')
    list_filter = ('group', 'person')

class TokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'person','date_created')

admin.site.register(Person, PersonAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EmailSchedule, EmailScheduleAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(GroupAutoParticipation, GroupAutoParticipationAdmin)
admin.site.register(Token, TokenAdmin)
