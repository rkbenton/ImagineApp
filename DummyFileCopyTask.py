"""
This is a useful class for testing.
"""
import time

from LongTaskABC import LongTaskABC


class DummyFileCopyTask(LongTaskABC):
    """
    Dummy implementation of a file copy task.
    """

    def __init__(self, job_id=None, fail: bool = False):
        """

        :param job_id: a unique id for this task. If None, one is generated.
        :param fail: if True, raise an exception at 50% completion.
        """
        super().__init__(job_id=job_id)
        self.fail = fail

    def execute(self) -> None:
        self._working = True
        try:
            # Simulate progress in 10 steps over 5 seconds.
            for i in range(1, 11):
                if self.fail and i > 5:
                    print("DummyFileCopyTask will fail now. ")
                    raise Exception("DummyFileCopyTask failed")
                if self._cancelled:
                    break
                time.sleep(0.5)
                self._progress = i * 10
            self._working = False
            self._success = True
        except Exception as e:
            self._failed = True
            self._failure = e
            self._working = False
