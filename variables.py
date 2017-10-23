# coding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

TASK_FUN_TYPE = [
    [1, u'celery_func'],
    [2, u' common_func'],
]

TASK_FUN_TYPE_MAP = {}
for t in TASK_FUN_TYPE:
    TASK_FUN_TYPE_MAP[t[1]] = t[0]

TASK_FUN_TYPE_DICT = {}
for l in TASK_FUN_TYPE:
    TASK_FUN_TYPE_DICT[l[0]] = l[1]
