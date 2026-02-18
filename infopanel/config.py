import yaml

DEFAULT_CONFIG = """
ledpanel:
  emulator: true

scheduler:
  widgets:
    - type: hafas_timetable
      params:
        location: "Ernst-Reuter-Platz"
        timezone: "Europe/Berlin"
        lines: ["U2", "245", "M45"]
      duration: 20

    - type: hafas_timetable
      params:
        location: "Berlin Zoologischer Garten"
        timezone: "Europe/Berlin"
        lines: ["S3", "S5", "S7", "S9"]
      duration: 20
"""

CONFIG = {}


def load_config(filename: str = "config.yaml"):
    global CONFIG

    try:
        with open(filename, "r") as f:
            CONFIG.update(yaml.safe_load(f))
    except FileNotFoundError:
        CONFIG.update(yaml.safe_load(DEFAULT_CONFIG))
