from abc import ABC, abstractmethod


class LongTaskABC(ABC):
    """
    The Command interface declares a method for executing a command.
    This is designed for long-running tasks.
    """

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def get_progress(self) -> int:
        """
        :return: The current progress of the command, from 0..100, inclusive.
        """
        pass

    @abstractmethod
    def cancel(self) -> None:
        """
        Cease working, if you are working.
        :return: Nothing.
        """
        pass

    @abstractmethod
    def is_working(self) -> bool:
        pass

    @abstractmethod
    def failed(self) -> bool:
        pass

    @abstractmethod
    def get_failure(self) -> Exception:
        pass
