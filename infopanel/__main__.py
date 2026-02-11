import logging

from .ledpanel import LEDPanel
from .scheduler import Scheduler


def main():
    logging.basicConfig(level=logging.INFO)

    panel = LEDPanel()
    panel.initialize()

    scheduler = Scheduler(
        config={
            "widgets": [
                {
                    "type": "hafas_timetable",
                    "params": {
                        "location": "Ernst-Reuter-Platz",
                        "timezone": "Europe/Berlin",
                        "lines": ["U2", "245", "M45"],
                    },
                    "duration": 20,
                },
                {
                    "type": "hafas_timetable",
                    "params": {
                        "location": "Berlin Zoologischer Garten",
                        "timezone": "Europe/Berlin",
                        "lines": ["S3", "S5", "S7", "S9"],
                    },
                    "duration": 20,
                },
            ],
        },
        panel=panel,
    )
    scheduler.run()


if __name__ == "__main__":
    main()
