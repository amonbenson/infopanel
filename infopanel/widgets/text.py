from dataclasses import dataclass

from ..ledpanel import LEDPanel
from .base import Widget


@dataclass
class TextWidget(Widget):
    def __init__(self, text: str = "Hello, World!"):
        super().__init__(text=text)

    def update(self, delta_time: float):
        pass

    def render(self, panel: LEDPanel):
        font = "regular"

        text = self._params["text"]
        lines = text.splitlines()

        line_height = panel.line_height(font)
        line_offset = -(len(lines) - 1) * panel.line_height(font) // 2

        for i, line in enumerate(lines):
            x = panel.width // 2
            y = panel.height // 2 + i * line_height + line_offset

            panel.draw_text(
                text=line,
                x=x,
                y=y,
                font=font,
                color=(255, 255, 255),
                halign="center",
                valign="center",
            )
