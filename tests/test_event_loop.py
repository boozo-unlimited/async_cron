import asyncio
import unittest

from async_cron.job import CronJob
from async_cron.schedule import Scheduler


class TestEventLoopHandling(unittest.TestCase):
    """Python >= 3.14 removed the implicit event loop creation of
    asyncio.get_event_loop() in the main thread (RuntimeError when no loop
    exists). CronJob and Scheduler must keep working outside of a running
    loop - historically they created and installed a loop themselves."""

    def tearDown(self):
        asyncio.set_event_loop(None)

    def test_cronjob_creates_event_loop_outside_running_loop(self):
        asyncio.set_event_loop(None)
        job = CronJob(name='loop_test')
        self.assertIsInstance(job.loop, asyncio.AbstractEventLoop)
        self.assertIs(asyncio.get_event_loop(), job.loop)

    def test_scheduler_creates_event_loop_outside_running_loop(self):
        asyncio.set_event_loop(None)
        scheduler = Scheduler(name='loop_test')
        self.assertIsInstance(scheduler.loop, asyncio.AbstractEventLoop)
        self.assertIs(asyncio.get_event_loop(), scheduler.loop)

    def test_explicit_loop_is_used(self):
        explicit_loop = asyncio.new_event_loop()
        try:
            job = CronJob(name='loop_test', loop=explicit_loop)
            scheduler = Scheduler(name='loop_test', loop=explicit_loop)
            self.assertIs(job.loop, explicit_loop)
            self.assertIs(scheduler.loop, explicit_loop)
        finally:
            explicit_loop.close()

    def test_running_loop_is_used_inside_coroutine(self):
        async def check_job():
            job = CronJob(name='loop_test')
            return asyncio.get_running_loop() is job.loop

        async def check_scheduler():
            scheduler = Scheduler(name='loop_test')
            return asyncio.get_running_loop() is scheduler.loop

        self.assertTrue(asyncio.run(check_job()))
        self.assertTrue(asyncio.run(check_scheduler()))


if __name__ == '__main__':
    unittest.main()
