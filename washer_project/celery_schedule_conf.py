from celery.schedules import crontab


CELERYBEAT_SCHEDULE = {
    'check-expired-reservations': {
        'task': 'reservations.tasks.check_expired_reservations',
        'schedule': crontab(minute='*/1'),
    },
    'create-next-week-day-reservations': {
        'task': 'reservations.tasks.create_next_week_day',
        'schedule': crontab(hour='4', minute='0'),
    },
}
