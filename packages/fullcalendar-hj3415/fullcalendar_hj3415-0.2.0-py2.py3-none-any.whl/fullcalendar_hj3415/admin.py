# admin.py
from django.contrib import admin
from .models import Calendar, Event, EventType

@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('modal_title', 'activate')
    list_filter = ('activate',)
    search_fields = ('modal_title',)

@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_of_event', 'calendar', 'event_type')
    list_filter = ('calendar', 'event_type', 'date_of_event')
    search_fields = ('title',)
    date_hierarchy = 'date_of_event'