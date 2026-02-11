import logging
import threading
from abc import ABC, abstractmethod
from typing import Callable

from ..ledpanel import LEDPanel


class Widget(ABC):
    def __init__(self, **params):
        self._params = params
        self._logger = logging.getLogger(self.__class__.__name__)

        self._render_requested = False

        self._running = False
        self._lock = threading.Lock()
        self._background_threads: list[threading.Thread] = []

    @property
    def params(self):
        return self._params

    @property
    def render_requested(self):
        return self._render_requested

    @property
    def running(self):
        return self._running

    def request_render(self):
        self._render_requested = True

    def clear_render_request(self):
        self._render_requested = False

    def register_background_thread(self, target: Callable, *args, **kwargs):
        if self._running:
            raise RuntimeError("Background threads must be registered before the widget is started")

        self._logger.info(f"Registering background thread: {target.__name__}")
        thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        self._background_threads.append(thread)

    def start(self):
        self._logger.info("Starting widget...")
        self.setup()

        self._running = True
        for thread in self._background_threads:
            thread.start()

    def stop(self):
        self._logger.info("Stopping widget...")
        self._running = False
        for thread in self._background_threads:
            thread.join(timeout=5)

        self.teardown()

    def setup(self):
        pass

    def teardown(self):
        pass

    def show(self):
        pass

    def hide(self):
        pass

    @abstractmethod
    def render(self, panel: LEDPanel, delta_time: float):
        raise NotImplementedError("Subclasses must implement render() method")
