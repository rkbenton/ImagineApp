import uuid
from abc import ABC, abstractmethod


class LongTaskABC(ABC):
    """
    This is our standard interface for any long-running job—whether it's copying files,
    processing images, or anything else—and your UI can interact with these jobs in
    a uniform way. It is, essentially, the Command Pattern.

    It defines the following methods:

    - execute(): Runs the job.
    - get_progress(): Returns an integer (0–100) representing job progress.
    - cancel(): Stops the job.
    - is_working(): Indicates if the job is currently running.
    - failed() and get_failure(): Allow error reporting.

    A task might be run asynchronously:
    ```python
    def start_task(self, task: LongTaskABC) -> str:
        self.tasks[task.get_job_id()] = task  # add to dictionary of tasks
        threading.Thread(target=task.execute).start()
        return task.get_job_id()
    ```
    """

    def __init__(self, job_id=None):
        """

        :param job_id: a unique identifier for the job; if None,
        a uuid will be generated and assigned.
        """
        self._working: bool = False
        self._success: bool = False  # completed 100%
        self._progress: int = 0
        self._cancelled: bool = False
        self._failed: bool = False
        self._failure: Exception = None
        self._job_id: str = job_id

        if self._job_id is None:
            self._job_id = str(uuid.uuid4())

    @abstractmethod
    def execute(self) -> None:
        """
        Example implementation:
        ```python
        self._working = True
        try:
            # Simulate progress in 10 steps over 5 seconds.
            for i in range(1, 11):
                if self._cancelled:
                    break
                time.sleep(0.5)
                self._progress = i * 10
            self._working = False
        except Exception as e:
            self._failed = True
            self._failure = e
            self._working = False
        ```

        :return: None
        """
        pass

    def get_progress(self) -> int:
        """
        :return: The current progress of the command, from 0..100, inclusive.
        """
        return self._progress

    def is_working(self) -> bool:
        return self._working

    def was_victorious(self) -> bool:
        return self._success

    def cancel(self) -> None:
        self._working = False
        self._cancelled = True

    def is_canceled(self) -> bool:
        return self._cancelled

    def failed(self) -> bool:
        self._working = False
        return self._failed

    def get_failure(self) -> Exception:
        return self._failure

    def get_job_id(self) -> str:
        return self._job_id
