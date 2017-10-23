# coding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
import time
from logging import getLogger
from threading import Event, Thread

logger = getLogger('common.logger')
debug, info, error, warning = (logger.debug, logger.info,
                               logger.error, logger.warning)


class Service(object):

    def __init__(self, scheduler):
        self.scheduler = scheduler

        self._is_shutdown = Event()
        self._is_stopped = Event()

    def __reduce__(self):
        return self.__class__, (self.scheduler,)

    def start(self, drift=-0.010):
        info('beat: Starting...')

        try:
            while not self._is_shutdown.is_set():
                interval = self.scheduler.tick()
                interval = interval + drift if interval else interval
                if interval and interval > 0:
                    debug('beat: Waking up %s.', interval)
                    time.sleep(interval)
                    self.scheduler.do_tasks()
        except (KeyboardInterrupt, SystemExit):
            error('service exit for KeyboardInterrupt, SystemExit!', exc_info=True)
            self._is_shutdown.set()
        except:
            error('service exit for not normal', exc_info=True)
            self._is_shutdown.set()
        finally:
            self.sync()

    def sync(self):
        self._is_stopped.set()

    def stop(self, wait=False):
        info('beat: Shutting down...')
        self._is_shutdown.set()
        wait and self._is_stopped.wait()  # block until shutdown done.


class BeatThreaded(Thread):
    def __init__(self,  *args, **kwargs):
        super(BeatThreaded, self).__init__()

        self.service = Service(*args, **kwargs)
        self.daemon = True
        self.name = 'Beat'

    def run(self):
        self.service.start()

    def stop(self):
        self.service.stop(wait=True)


def test_func(*args, **kwargs):
    debug("test_func run : args:%s ,kwargs:%s", args, kwargs)

if __name__ == '__main__':
    import threading
    from hmy_db_beat.service import BeatThreaded
    from hmy_db_beat.scheduler import Scheduler
    s = Scheduler(50)
    t = BeatThreaded(s)
    t.start()
    event = threading.Event()
    event.set()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print "main KeyboardInterrupt"
        event.clear()
        t.stop()



