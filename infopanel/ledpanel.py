import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING


try:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
    if TYPE_CHECKING:
        from RGBMatrixEmulator.emulation.canvas import Canvas
except ImportError:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics  # type: ignore


@dataclass
class LEDPanelConfig:
    rows: int = 64
    cols: int = 128
    hardware_mapping: str = "regular"


class LEDPanel:
    def __init__(self, config: LEDPanelConfig | None = None):
        self._config = config or LEDPanelConfig()

        self._matrix: RGBMatrix | None = None
        self._canvas: Canvas | None = None

        self._load_fonts({
            "regular": "tb-8.bdf",
            "bold": "tb-8-bold.bdf",
        })

    def _load_fonts(self, files: dict[str, str]):
        self._fonts = {}

        for name, filename in files.items():
            path = Path(__file__).parent / "fonts" / filename
            if not path.exists():
                raise FileNotFoundError(f"Font file '{filename}' not found in 'fonts' directory")

            font = graphics.Font()
            font.LoadFont(path.as_posix())
            self._fonts[name] = font

    def _get_font(self, name: str) -> graphics.Font:
        if name not in self._fonts:
            raise ValueError(f"Font '{name}' not found. Use one of: {', '.join(self._fonts.keys())}")

        return self._fonts[name]

    @property
    def matrix(self) -> RGBMatrix:
        if self._matrix is None:
            raise RuntimeError("LEDPanel not initialized. Call initialize() first.")
        return self._matrix

    @property
    def canvas(self) -> Canvas:
        if self._canvas is None:
            raise RuntimeError("LEDPanel not initialized. Call initialize() first.")
        return self._canvas

    @property
    def width(self) -> int:
        return self._config.cols

    @property
    def height(self) -> int:
        return self._config.rows

    def initialize(self):
        options = RGBMatrixOptions()
        options.rows = self._config.rows
        options.cols = self._config.cols
        options.hardware_mapping = self._config.hardware_mapping

        self._matrix = RGBMatrix(options=options)
        self._canvas = self._matrix.CreateFrameCanvas()

    def render(self):
        self.matrix.SwapOnVSync(self._canvas)

    def character_width(self, font: str, char: str) -> int:
        return self._get_font(font).CharacterWidth(ord(char))

    def line_height(self, font: str) -> int:
        return self._get_font(font).height

    def draw_text(self, text: str, x: int, y: int, *, font: str = "regular", color: tuple[int, int, int] = (255, 255, 255), halign: str = "left", valign: str = "top"):
        font_obj = self._get_font(font)

        # Get text dimensions for alignment
        text_width = sum(font_obj.CharacterWidth(ord(c)) for c in text)
        text_baseline = font_obj.baseline

        # Adjust x based on horizontal alignment
        if halign == "center":
            x -= text_width // 2
        elif halign == "right":
            x -= text_width

        # Adjust y based on vertical alignment
        if valign == "center":
            y += text_baseline // 2
        elif valign == "top":
            y += text_baseline

        graphics.DrawText(self.canvas, font_obj, x, y, graphics.Color(*color), text)
