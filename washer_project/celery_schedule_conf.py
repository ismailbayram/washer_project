from celery.schedules import crontab


CELERYBEAT_SCHEDULE = {
    'check-expired-reservations': {
        'task': 'reservations.tasks.check_expired_reservations',
        'schedule': crontab(minute='*/30'),
        'args': (),
    },
}
