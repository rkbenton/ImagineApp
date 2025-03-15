import threading

from LongTaskABC import LongTaskABC


class JobManager:
    def __init__(self):
        self.tasks:dict[LongTaskABC] = {}

    def start_task(self, task: LongTaskABC) -> str:
        """
        Kick off a task in a thread, and store the task in a dictionary
        keyed by the task's job_id.
        :param task: The task to start
        :return: the job_id
        """
        self.tasks[task.get_job_id()] = task  # add to dictionary of tasks
        threading.Thread(target=task.execute).start()
        return task.get_job_id()

    def get_task(self, job_id: str) -> LongTaskABC | None:
        """
        Retrieve a task by its job_id.
        :param job_id: the unique id of the job.
        :return: the task if JobManager is tracking it, or None otherwise.
        """
        if not(job_id in self.tasks):
            return None
        task = self.tasks.get(job_id)
        return task

    def remove_task(self, job_id: str) -> None:
        del self.tasks[job_id]