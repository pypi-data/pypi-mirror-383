from datetime import timedelta
from django import template
from django.utils import timezone

from ..models import Calendar, Event

register = template.Library()

@register.inclusion_tag("fullcalendar_hj3415/_load.html")
def show_calendar(modal_id="calendarModal", auto_open=True):
    calendar1 = Calendar.objects.filter(activate=True).first()
    events_qs = Event.objects.none()
    if calendar1:
        events_qs = (
            Event.objects.filter(calendar=calendar1)
            .select_related('event_type')
            .order_by('date_of_event', 'title')
        )

    context = {
        "modal_id": modal_id,
        "auto_open": auto_open,
        "dont_show_again": "다시보지않기",
        "calendar": calendar1,
        "events": events_qs,
        "default_date": set_default_date().date().isoformat(),
    }
    return context

def set_default_date(date=25):
    """
    full calendar의 defaultDate 설정.
    date일 이후면 +7일로 다음달 유도, 아니면 오늘.
    """
    today = timezone.localdate()
    if today.day >= date:
        return timezone.now() + timedelta(days=7)
    return timezone.now()