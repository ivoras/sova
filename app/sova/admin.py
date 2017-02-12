from django.contrib import admin

from .models import Person, Group, Event, EmailSchedule

class EmailScheduleInline(admin.StackedInline):
    model = EmailSchedule

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name',)
    inlines = ( EmailScheduleInline, )

class EmailScheduleAdmin(admin.ModelAdmin):
    list_display = ('date', 'event', 'name', 'subject')
    list_filter = ('date', 'sent', 'group')
    search_fields = ('name', 'group__name', 'event__name')

admin.site.register(Person)
admin.site.register(Group)
admin.site.register(Event, EventAdmin)
admin.site.register(EmailSchedule, EmailScheduleAdmin)