import logging

from .config import CONFIG
from .ledpanel import LEDPanel
from .scheduler import Scheduler


def main():
    logging.basicConfig(level=logging.INFO)

    panel = LEDPanel(CONFIG.get("ledpanel", {}))
    panel.initialize()

    scheduler = Scheduler(
        config=CONFIG.get("scheduler", {}),
        panel=panel,
    )
    scheduler.run()


if __name__ == "__main__":
    main()
