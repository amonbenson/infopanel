from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from requests.adapters import HTTPAdapter, Retry

from ..ledpanel import LEDPanel
from .base import Widget


@dataclass
class Location:
    id: str
    name: str

    @staticmethod
    def from_hafas(loc: dict):
        return Location(
            id=loc["lid"],
            name=loc["name"].replace("(Berlin)", "").strip(),
        )


@dataclass
class Departure:
    id: str
    name: str
    direction: str
    cancelled: bool = False
    minutes: int = 0

    @staticmethod
    def from_hafas(dep: dict, common: dict, now_minutes: int = 0):
        id = dep["jid"]
        name = common["prodL"][dep["prodX"]]["name"]
        direction = dep["dirTxt"].replace("(Berlin)", "").strip()
        cancelled = dep["stbStop"].get("dCncl", False)

        # Calculate minutes until departure
        timestamp = dep["stbStop"].get("dTimeR", dep["stbStop"]["dTimeS"])
        departure_minutes = hafas_timestamp_to_minutes(timestamp)
        minutes = departure_minutes - now_minutes

        # Account for day-shift
        if minutes >= 12 * 60:
            minutes -= 24 * 60

        return Departure(
            id=id,
            name=name,
            direction=direction,
            cancelled=cancelled,
            minutes=minutes,
        )


@dataclass
class Him:
    id: str
    title: str
    body: str

    @staticmethod
    def from_hafas(h: dict) -> "Him":
        return Him(
            id=h["hid"],
            title=h["head"],
            body=h["text"],
        )


def hafas_timestamp_to_minutes(ts: str):
    if len(ts) == 8:
        days = int(ts[0:2])
        ts = ts[2:]
    else:
        days = 0

    hours = int(ts[0:2])
    minutes = int(ts[2:4])
    _seconds = int(ts[4:6])

    return days * 24 * 60 + hours * 60 + minutes


class HafasAPI:
    ENDPOINT = "https://bvg-apps-ext.hafas.de/gate"
    BODY = {
        "id": "724muxsmmmsph34k",
        "ver": "1.72",
        "lang": "deu",
        "auth": {
            "type": "AID",
            "aid": "dVg4TZbW8anjx9ztPwe2uk4LVRi9wO",
        },
        "client": {
            "id": "VBB",
            "type": "WEB",
            "name": "webapp",
            "l": "vs_webapp",
            "v": 10004,
        },
        "formatted": False,
    }
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:147.0) Gecko/20100101 Firefox/147.0"

    def __init__(self):
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def request(self, data: dict):
        body = {
            **self.BODY,
            "svcReqL": [data],
        }

        res = self.session.post(self.ENDPOINT, json=body, headers={"User-Agent": self.USER_AGENT})
        res.raise_for_status()

        return res.json()

    def search_location(self, query: str) -> Location | None:
        res = self.request({
            "meth": "LocMatch",
            "req": {
                "input": {
                    "field": "S",
                    "loc": {
                        "name": query,
                        "type": "S",
                    },
                },
            },
        })

        locations = res["svcResL"][0]["res"]["match"]["locL"]
        if not locations:
            return None

        location = locations[0]
        return Location.from_hafas(location)

    def list_departures(self, location_id: str, top: int = 10, now_minutes: int = 0) -> tuple[list[Departure], list[Him]]:
        res = self.request({
            "meth": "StationBoard",
            "req": {
                "jnyFltrL": [
                    {
                        "type": "PROD",
                        "mode": "INC",
                        "value": 127,
                    },
                ],
                "stbLoc": {
                    "lid": location_id,
                },
                "type": "DEP",
                "sort": "PT",
                "maxJny": top,
            },
        })

        common = res["svcResL"][0]["res"]["common"]

        hafas_departures = res["svcResL"][0]["res"]["jnyL"]
        departures = [Departure.from_hafas(d, common, now_minutes) for d in hafas_departures]

        # remove past or cancelled departures and sort by time till departures
        departures = [d for d in departures if not d.cancelled and d.minutes > 0]
        departures.sort(key=lambda d: d.minutes)

        # Get unique hims
        hafas_hims = common.get("himL", [])
        hafas_hims = list({him["hid"]: him for him in hafas_hims}.values())
        hims = [Him.from_hafas(h) for h in hafas_hims]

        return departures, hims


@dataclass
class HafasWidget(Widget):
    def __init__(self, location: str, timezone: str = "UTC"):
        super().__init__(location=location, timezone=timezone)

        # Store the timezone info
        self._timezone = ZoneInfo(timezone)

        # Create the Hafas API
        self._api = HafasAPI()

        # Search for the provided location
        self._location: Location | None = None
        self._departures: list[Departure] = []
        self._hims: list[Him] = []

        # Initial fetch
        self._fetch()

    def _current_minutes(self) -> int:
        now = datetime.now(self._timezone)
        return now.hour * 60 + now.minute

    def _fetch(self):
        # Fetch location
        if self._location is None:
            self._location = self._api.search_location(self._params["location"])
            if self._location is None:
                raise ValueError(f"Location '{self._params['location']}' not found")

        # Fetch departures and hims
        now_minutes = self._current_minutes()
        self._departures, self._hims = self._api.list_departures(
            location_id=self._location.id,
            now_minutes=now_minutes,
            top=20,
        )

    def update(self, delta_time: float):
        pass

    def render(self, panel: LEDPanel):
        font = "regular"
        color = (255, 128, 0)

        # Draw the location
        location = self._location.name if self._location else "Unknown location"
        panel.draw_text(
            text=location,
            x=panel.width // 2,
            y=0,
            font=font,
            color=color,
            halign="center",
            valign="top",
        )

        # Draw each departure
        max_departures = panel.height // panel.line_height(font) - 1
        for i, departure in enumerate(self._departures[:max_departures]):
            y = (i + 1) * panel.line_height(font)

            # Departure line name
            panel.draw_text(
                text=departure.name,
                x=1,
                y=y,
                font="bold",
                color=color,
                halign="left",
                valign="top",
            )

            # Departure line direction/destination
            panel.draw_text(
                text=departure.direction[:18],
                x=25,
                y=y,
                font=font,
                color=color,
                halign="left",
                valign="top",
            )

            # Departure time till departure
            minutes = max(0, min(99, departure.minutes))
            panel.draw_text(
                text=f"{minutes}'",
                x=panel.width - 1,
                y=y,
                font=font,
                color=color,
                halign="right",
                valign="top",
            )
