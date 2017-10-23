# coding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import


def is_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    return True


class TimePlan(object):
    def __init__(self, minute='*', hour='*'):
        self.hour = self._expand_cronspec(hour, 24)
        self.minute = self._expand_cronspec(minute, 60)

    @staticmethod
    def _expand_cronspec(cronspec, max_, min_=0):

        if isinstance(cronspec, int):
            result = cronspec
        elif isinstance(cronspec, str):
            result = int(cronspec)
        else:
            raise TypeError('int or str is required')
        if result > max_:
            raise ValueError('value is to big ,max :%s' % max_)
        if result < min_:
            raise ValueError('value is to small ,min :%s' % min_)
        return result

