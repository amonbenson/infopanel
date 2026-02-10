import logging
from abc import ABC, abstractmethod

from ..ledpanel import LEDPanel


class Widget(ABC):
    def __init__(self, **params):
        self._params = params
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def update(self, delta_time: float):
        raise NotImplementedError("Subclasses must implement update() method")

    @abstractmethod
    def render(self, panel: LEDPanel):
        raise NotImplementedError("Subclasses must implement render() method")
