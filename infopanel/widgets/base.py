import logging
from abc import ABC, abstractmethod

from ..ledpanel import LEDPanel


class Widget(ABC):
    def __init__(self, **params):
        self._params = params
        self._logger = logging.getLogger(self.__class__.__name__)

        self._render_requested = False

    @property
    def params(self):
        return self._params

    @property
    def render_requested(self):
        return self._render_requested

    def request_render(self):
        self._render_requested = True

    def clear_render_request(self):
        self._render_requested = False

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
