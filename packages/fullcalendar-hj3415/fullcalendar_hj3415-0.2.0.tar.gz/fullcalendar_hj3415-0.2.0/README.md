# fullcalendar-hj3415

fullcalendar v4 를 이용해서 월별 일정 모달창을 띄우는 모듈.


1. 프로젝트의 settings.py 에 추가한다.
```python
INSTALLED_APPS = [
    'fullcalendar_hj3415',
]
```

2. makemigration, migrate 실행

3. 사용 위치의 html에 작성한다.
```html
{% load fullcalendar_tags %}
...
{% show_calendar %}
```