import logging

from .ledpanel import LEDPanel
from .widgets import HafasWidget


def main():
    logging.basicConfig(level=logging.INFO)

    panel = LEDPanel()
    panel.initialize()

    widget = HafasWidget("Neue Filandastr", timezone="Europe/Berlin")
    widget.render(panel)

    panel.render()

    try:
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
