from queue import Empty, Queue
from threading import Thread
from typing import Any, Callable


class TkAsyncTaskRunner:

    _POLL_INTERVAL_MS = 50

    def __init__(
        self,
        scheduler
    ):
        self._scheduler = scheduler

    def run(
        self,
        task: Callable[[], Any],
        on_success: Callable[[Any], None],
        on_error: Callable[[Exception], None]
    ) -> None:

        result_queue = Queue(
            maxsize=1
        )

        worker = Thread(
            target=self._execute,
            args=(
                task,
                result_queue
            ),
            name="sistemafrete-background-task"
        )

        worker.start()

        self._poll(
            result_queue=result_queue,
            on_success=on_success,
            on_error=on_error
        )

    @staticmethod
    def _execute(
        task,
        result_queue
    ) -> None:

        try:

            result = task()

        except Exception as error:

            result_queue.put(
                (
                    False,
                    error
                )
            )

            return

        result_queue.put(
            (
                True,
                result
            )
        )

    def _poll(
        self,
        result_queue,
        on_success,
        on_error
    ) -> None:

        try:

            success, payload = (
                result_queue.get_nowait()
            )

        except Empty:

            self._scheduler.after(
                self._POLL_INTERVAL_MS,
                self._poll,
                result_queue,
                on_success,
                on_error
            )

            return

        if success:

            on_success(
                payload
            )

            return

        on_error(
            payload
        )