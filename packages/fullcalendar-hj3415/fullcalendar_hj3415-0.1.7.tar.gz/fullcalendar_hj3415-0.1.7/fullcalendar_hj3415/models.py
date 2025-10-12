
from django.db import models
from django.db.models import Q

DEFAULT_COLOR = "#3788d8"

class EventType(models.Model):
    name = models.CharField('event_type', max_length=20, unique=True)
    color = models.CharField('color', max_length=7, default=DEFAULT_COLOR,
                             help_text="HEX 코드 형식 예: #FF0000")
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "스케쥴 타입"

class Calendar(models.Model):
    modal_title = models.CharField('calendar_name', default="휴진안내", max_length=40,
                                   help_text=r"줄넘기기 : \n")
    activate = models.BooleanField(default=False, help_text="활성창 1개만 가능")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['activate'],
                condition=Q(activate=True),
                name='unique_active_calendar'
            )
        ]
        ordering = ['-activate', 'modal_title']
        verbose_name = "달력"
        verbose_name_plural = "달력 목록"

    def __str__(self):
        return self.modal_title

class Event(models.Model):
    title = models.CharField('title', default="휴진", max_length=20)
    date_of_event = models.DateField(db_index=True)
    calendar = models.ForeignKey(
        Calendar,
        related_name='events',   # ← 기존 'calendar'에서 의미 있는 이름으로 변경
        on_delete=models.PROTECT,
    )
    event_type = models.ForeignKey(
        EventType,
        related_name='events',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['date_of_event']),
            models.Index(fields=['calendar', 'date_of_event']),
        ]
        ordering = ['date_of_event', 'title']
        verbose_name = "스케쥴"
        verbose_name_plural = "스케쥴 목록"

    def __str__(self):
        return f"{self.title}/{self.date_of_event}"

    @property
    def color_hex(self) -> str:
        # 이벤트 타입이 없을 때도 안전하게 색상 제공
        return (self.event_type.color if self.event_type else DEFAULT_COLOR)