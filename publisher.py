# coding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import numbers

from django.utils import timezone
from kombu import Connection, Producer, Exchange, Queue
from kombu.common import Broadcast
from kombu.utils import uuid
from datetime import timedelta
from celery.utils.timeutils import to_utc

INT_MIN = -2147483648


class CustomPublisher(object):
    retry = False
    task_queue = None
    utc = True
    channel = None
    publisher = None

    def __init__(self, ampq_url):
        self.connection = Connection(ampq_url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.release()

    def init_task_queue(self, exchange_name, queue_name, routing_key, exchange_type='direct'):
        self.task_queue = Queue(queue_name, Exchange(exchange_name, type=exchange_type), routing_key=routing_key)

    def publish(self, body, declare):

        if not self.connection.connected:

            self.connection.connect()
            if not self.connection.connected:
                raise StandardError('amqp连接失败')
        if self.task_queue is None:
            raise StandardError('task_queue 还没有初始化')
        self.channel = self.connection.channel()
        self.publisher = Producer(self.channel)
        self.publisher.publish(body, retry=True, exchange=self.task_queue.exchange, routing_key=self.task_queue.routing_key, declare=declare)


    def _verify_seconds(self, s, what):
        if s < INT_MIN:
            raise ValueError('%s is out of range: %r' % (what, s))
        return s

    def publish_task(self, task_name, task_args=None, task_kwargs=None,
                     countdown=None, eta=None, task_id=None,
                     expires=None, retry=None,
                     declare=None, now=None
                     ):
        """Send task message."""
        retry = self.retry if retry is None else retry

        if declare is None and self.task_queue and not isinstance(self.task_queue, Broadcast):
            declare = [self.task_queue]

        task_id = task_id or uuid()
        task_args = task_args or []
        task_kwargs = task_kwargs or {}
        if not isinstance(task_args, (list, tuple)):
            raise ValueError('task args must be a list or tuple')
        if not isinstance(task_kwargs, dict):
            raise ValueError('task kwargs must be a dictionary')
        if countdown:  # Convert countdown to ETA.
            self._verify_seconds(countdown, 'countdown')
            now = now or timezone.now()
            eta = now + timedelta(seconds=countdown)
            if self.utc:
                eta = to_utc(eta).astimezone(timezone.utc)
        if isinstance(expires, numbers.Real):
            self._verify_seconds(expires, 'expires')
            now = now or timezone.now()
            expires = now + timedelta(seconds=expires)
            if self.utc:
                expires = to_utc(expires).astimezone(timezone.utc)
        eta = eta and eta.isoformat()
        expires = expires and expires.isoformat()

        body = {
             'args': task_args,
             'callbacks': None,
             'chord': None,
             'errbacks': None,
             'eta': eta,
             'expires': expires,
             'id': task_id,
             'kwargs': task_kwargs,
             'retries': retry or 0,
             'task': task_name,
             'taskset': task_id,
             'timelimit': (None, None),
             'utc': self.utc
        }
        self.publish(body, declare)
