from django.contrib import admin

from .models import Person, Group, Event, EmailSchedule, Participation

class EmailScheduleInline(admin.StackedInline):
    model = EmailSchedule

class ParticipationInline(admin.StackedInline):
    model = Participation

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name',)
    inlines = ( EmailScheduleInline, ParticipationInline )

class EmailScheduleAdmin(admin.ModelAdmin):
    list_display = ('date', 'event', 'name', 'subject', 'sent')
    list_filter = ('date', 'sent', 'group')
    search_fields = ('name', 'group__name', 'event__name')

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('person', 'event', 'grade', 'participated')

admin.site.register(Person)
admin.site.register(Group)
admin.site.register(Event, EventAdmin)
admin.site.register(EmailSchedule, EmailScheduleAdmin)
admin.site.register(Participation, ParticipationAdmin)