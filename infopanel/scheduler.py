import datetime
import logging
import time

from infopanel.ledpanel import LEDPanel
from infopanel.widgets import WIDGETS, Widget


class Scheduler:
    def __init__(self, config: dict, panel: LEDPanel):
        self._config = config
        self._panel = panel
        self._logger = logging.getLogger(self.__class__.__name__)

        self._widgets = []
        self._running = False

        self._current_widget_index: int | None = None
        self._current_widget_switch_time: datetime.datetime = datetime.datetime.now()

        self._initialize_widgets()

    @property
    def current_widget_config(self) -> dict:
        if self._current_widget_index is None:
            return {}

        return self._config["widgets"][self._current_widget_index]

    @property
    def current_widget(self) -> Widget | None:
        if self._current_widget_index is None:
            return None

        return self._widgets[self._current_widget_index]

    def _initialize_widgets(self):
        self._logger.info("Initializing widgets...")

        for config in self._config.get("widgets", []):
            # Get the type of widget
            widget_type = config.get("type")
            widget_class = WIDGETS.get(widget_type)
            if widget_class is None:
                raise ValueError(f"Unknown widget type: {widget_type}")

            # Instantiate a new instance
            widget_params = config.get("params", {})
            widget = widget_class(**widget_params)
            self._widgets.append(widget)

        if not self._widgets:
            raise ValueError("No widgets configured")

    def _next_widget_index(self) -> int:
        if self._current_widget_index is None:
            return 0

        return (self._current_widget_index + 1) % len(self._widgets)

    def _reset_next_widget_switch_time(self):
        assert self.current_widget_config is not None
        duration = self.current_widget_config.get("duration", 10)
        self._current_widget_switch_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)

    def _switch_widget(self):
        next_widget_index = self._next_widget_index()

        # No need to switch if it's the same widget
        if next_widget_index == self._current_widget_index:
            self._reset_next_widget_switch_time()
            return

        self._logger.info("Switching to next widget...")

        # Hide the current widget
        if self.current_widget is not None:
            self.current_widget.hide()

        # Update the current widget index and reset the switch time
        self._current_widget_index = next_widget_index
        self._reset_next_widget_switch_time()

        # Show the widget and request an initial render
        assert self.current_widget is not None
        self.current_widget.show()
        self.current_widget.request_render()

    def run(self):
        self._logger.info("Starting scheduler...")

        self._running = True

        # Setup all widgets
        for widget in self._widgets:
            widget.setup()

        try:
            # Show the first widget
            self._switch_widget()

            last_render_time = datetime.datetime.now()

            update_rate = self._config.get("update_rate", 1 / 30)  # Default to 30 updates per second
            while self._running:
                now = datetime.datetime.now()

                # Switch to the next widget if the time has come
                if self._current_widget_switch_time <= now:
                    self._switch_widget()
                    last_render_time = now

                # Render the current widget if it has requested a render
                assert self.current_widget is not None
                if self.current_widget.render_requested:
                    delta_time = (now - last_render_time).total_seconds()
                    self.current_widget.render(self._panel, delta_time)
                    self._panel.swap()
                    last_render_time = now

                time.sleep(update_rate)
        finally:
            self._logger.info("Stopping scheduler...")

            # Teardown all widgets
            for widget in self._widgets:
                widget.teardown()
