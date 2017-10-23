# coding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

from logging import getLogger
import traceback
import json
import os

from django.utils import timezone

from .models import TaskScheduleConfig
from .utils import get_interval_for_seconds
from .publisher import CustomPublisher
logger = getLogger('common.logger')

debug, info, error, warning = (logger.debug, logger.info,
                               logger.error, logger.warning)


class Scheduler(object):
    def __init__(self, max_interval=None):
        self.max_interval = max_interval or 500

    def tick(self):
        return self.get_next_interval()

    def update_task_due(self, task, is_due=False):
        task.next_due = is_due
        task.save()

    def get_next_interval(self):
        next_run_times = []
        tasks = list(TaskScheduleConfig.objects.filter(enable=True).all())
        for task in tasks:
            next_run_time = get_interval_for_seconds(task.pk, task.last_run_at, task.schedule, self.max_interval)
            next_run_times.append(next_run_time)
        min_interval = min(next_run_times + [self.max_interval])
        min_index = [index for index, t in enumerate(next_run_times) if t == min_interval]
        min_tasks = [tasks[index] for index in min_index if index < len(tasks)]
        [self.update_task_due(task, True) for task in min_tasks]
        return min_interval

    def do_tasks(self):
        tasks = TaskScheduleConfig.objects.filter(enable=True, next_due=True).all()

        for task in tasks:
            try:
                self.apply_async(task.task_func, task.func_args, task.func_kwargs, task.queue, task.exchange, task.routing_key, task.amqp_path)
            except Exception as exc:
                error('Message Error: %s\n%s', exc, traceback.format_stack(), exc_info=True)
                continue
            finally:
                task.next_due = False
                task.last_run_at = timezone.now()
                task.save()

    def apply_async(self, task_str, func_args, func_kwargs, queue, exchange, routing_key, amqp_path):
        args_list = func_args.replace(' ', '').split(',')
        if '' in args_list:
            args_list.remove('')
        assert isinstance(args_list, list)
        args = tuple(args_list)
        kwargs = json.loads(func_kwargs)
        if amqp_path.startswith('amqp'):
            amqp_url = amqp_path
        elif amqp_path.startswith('env'):
            env_path = amqp_path.split(':')[1]
            amqp_url = os.environ.get(env_path)
        else:
            raise ValueError('amqp_path 格式不正确')
        if not amqp_url:
            raise ValueError('amqp_path 为空')

        with CustomPublisher(amqp_url) as p:
            p.init_task_queue(exchange, queue, routing_key)
            try:
                p.publish_task(task_str, args, kwargs)
            except:
                error('发布任务失败', exc_info=True)


