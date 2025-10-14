"""Task manager for subscriber tasks."""

from anyio import create_task_group
from anyio.abc import TaskGroup

from fastpubsub.concurrency.tasks import PubSubPollTask
from fastpubsub.logger import logger
from fastpubsub.pubsub.subscriber import Subscriber


class AsyncTaskManager:
    """Public-facing controller for managing a fleet of subscriber tasks."""

    def __init__(self) -> None:
        """Initializes the AsyncTaskManager."""
        self._tasks: list[PubSubPollTask] = []
        self._task_group: TaskGroup | None = None

    async def create_task(self, subscriber: Subscriber) -> None:
        """Registers a subscriber configuration to be managed."""
        self._tasks.append(PubSubPollTask(subscriber))

    async def start(self) -> None:
        """Starts the subscribers tasks process using a task group."""
        self._task_group = await create_task_group().__aenter__()
        for task in self._tasks:
            self._task_group.start_soon(task.start)

        logger.debug(f"Started tasks for subscribers {self._tasks}")

    async def alive(self) -> dict[str, bool]:
        """Checks if the tasks are alive.

        Returns:
            A dictionary mapping task names to their liveness status.
        """
        liveness: dict[str, bool] = {}
        for task in self._tasks:
            liveness[task.subscriber.name] = task.task_alive()
        return liveness

    async def ready(self) -> dict[str, bool]:
        """Checks if the tasks are ready.

        Returns:
            A dictionary mapping task names to their readiness status.
        """
        readiness: dict[str, bool] = {}
        for task in self._tasks:
            readiness[task.subscriber.name] = task.task_ready()
        return readiness

    async def shutdown(self) -> None:
        """Terminates the manager process and all its children gracefully."""
        if self._task_group:
            self._task_group.cancel_scope.cancel()
            await self._task_group.__aexit__(None, None, None)
