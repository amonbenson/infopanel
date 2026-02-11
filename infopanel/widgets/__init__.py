from .base import Widget as Widget
from .hafas_timetable import HafasTimetable as HafasTimetable
from .text import TextWidget as TextWidget

WIDGETS = {
    "hafas_timetable": HafasTimetable,
    "text": TextWidget,
}
