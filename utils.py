# coding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from datetime import timedelta, datetime
from django.utils import timezone


from celery.schedules import crontab
from .models import TaskScheduleConfig


def get_interval_for_seconds(task_pk, task_last_run_time, task_schedule, max_interval):
    schedule = eval(task_schedule)
    task = TaskScheduleConfig.objects.get(pk=task_pk)
    assert isinstance(task_last_run_time, datetime)
    now = timezone.now()
    next_time = now
    if isinstance(schedule, timedelta):
        next_time = task_last_run_time + schedule
        # 有可能next_time < now
        if next_time < now:
            task.last_run_at = now
            task.save()
            return schedule.seconds
    elif isinstance(schedule, crontab):
        is_due, next_time_to_run = schedule.is_due(task_last_run_time)
        return next_time_to_run
    if next_time >= now:
        return (next_time - now).seconds
    else:
        return max_interval
