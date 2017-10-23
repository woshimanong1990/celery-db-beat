# coding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

from django.db import models
from .variables import TASK_FUN_TYPE


class TaskScheduleConfig(models.Model):
    name = models.CharField(max_length=50, default='',  verbose_name='任务名称')
    task_func = models.CharField(max_length=100, default='', verbose_name='具体任务')
    queue = models.CharField(max_length=100, default='', verbose_name='任务queue')
    exchange = models.CharField(max_length=100, default='', verbose_name='任务exchange')
    routing_key = models.CharField(max_length=100, default='', verbose_name='routing_key')
    amqp_path = models.CharField(max_length=100, default='', verbose_name='amqp_path')
    enable = models.BooleanField(default=True, verbose_name='是否可用')
    last_run_at = models.DateTimeField(auto_now_add=True, verbose_name='上次运行时')
    schedule = models.CharField(max_length=100, default='', verbose_name='时间计划')
    next_due = models.BooleanField(default=False, verbose_name='下次是否执行')
    func_args = models.CharField(max_length=100, default='', verbose_name='位置参数')
    func_kwargs = models.CharField(max_length=100, default='{}', verbose_name='关键字参数')

    def __unicode__(self):
        return self.name

    class Meta(object):
        verbose_name = '任务计划'
        verbose_name_plural = '任务计划'