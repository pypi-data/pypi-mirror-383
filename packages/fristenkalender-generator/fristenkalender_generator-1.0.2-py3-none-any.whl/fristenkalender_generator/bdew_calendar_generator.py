"""
This module can produce a list of calendar entries with bdew Fristen
"""

import dataclasses
import re
import sys
from calendar import monthrange

try:
    from datetime import UTC
except ImportError:
    if sys.version_info >= (3, 11):
        raise
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Literal, Optional, Union

from bdew_datetimes.periods import get_nth_working_day_of_month, get_previous_working_day
from icalendar import Calendar, Event  # type: ignore[import-untyped]

LwtLabel = Union[Literal["LWT"], Literal["3LWT"]]
Label = Union[
    Literal["5WT"],
    Literal["10WT"],
    Literal["12WT"],
    Literal["14WT"],
    Literal["16WT"],
    Literal["17WT"],
    Literal["18WT"],
    Literal["20WT"],
    Literal["21WT"],
    Literal["26WT"],
    Literal["30WT"],
    Literal["42WT"],
    LwtLabel,
]


class FristenType(Enum):
    """
    This class represents a type of a Frist
    """

    MABIS = "MABIS"
    GPKE = "GPKE"
    GELI = "GELI"
    KOV = "KOV"


_DAYS_AND_LABELS: dict[int, Label] = {
    5: "5WT",
    10: "10WT",
    12: "12WT",
    14: "14WT",
    16: "16WT",
    17: "17WT",
    18: "18WT",
    20: "20WT",
    21: "21WT",
    26: "26WT",
    30: "30WT",
    42: "42WT",
    0: "LWT",
    3: "3LWT",
}

_month_mapping: dict[int, str] = {
    1: "Januar",
    2: "Februar",
    3: "März",
    4: "April",
    5: "Mai",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Dezember",
}

_24hLfwKeyDate = date(2025, 6, 6)


@dataclasses.dataclass(unsafe_hash=True)
class FristWithAttributes:
    """
    This class represents a Frist with its attributes
    """

    date: date  #: = date(y,m,d)
    label: Label  #: can be for example '5WT' (5 Werktage des Liefermonats)
    ref_not_in_the_same_month: Optional[
        int
    ]  #: None if the Frist is in the same month as the ref. date, otherwise is a month number when the Frist started
    description: str  #: contains  specific description of each Frist


@dataclasses.dataclass(unsafe_hash=True)
class FristWithAttributesAndType(FristWithAttributes):
    """
    This class represents a Frist with a type
    """

    fristen_type: FristenType


_fristen_type_to_label_mapping: dict[str, list[Label]] = {
    FristenType.MABIS.value: ["5WT", "12WT", "17WT", "18WT", "20WT", "30WT", "42WT", "LWT"],
    FristenType.GELI.value: ["16WT"],
    FristenType.KOV.value: ["5WT", "10WT", "12WT", "14WT", "17WT", "18WT", "20WT", "21WT", "26WT"],
    FristenType.GPKE.value: ["3LWT"],
}
"""
maps a fristen type to  different fristen associated with the type
"""

specific_description: dict[Label, str] = {
    "5WT": (
        "Versand der BG-SummenZR (Kat B.)(ÜNB ⟶ NB)\n"
        "Versand Netzzeitreihen (VNB ⟶ BIKO)\n"
        "Abrechnungs-ZR endg. BRW (VNB ⟶ LF)\n"
    ),
    "10WT": "Eingang Netzzeitreihen (VNB ⟶ VNB)",
    "12WT": (
        "BK-SummenZR (VNB/ÜNB ⟶ BIKO & BIKO ⟶ BKV)\n"
        "LF-SummenZR (VNB ⟶ LF (bei Zuordnungsermächt.))\n"
        "BK-Summen vorl./endg. BRW (VNB ⟶ MGV)\n"
    ),
    "14WT": "BK-Summen vorl./endg. BRW (MGV ⟶ BKV)",
    "16WT": "Zuordnungslisten (VNB ⟶ LF)",
    "17WT": ("BK-Zuordnungsliste (VNB ⟶ BKV)\n" "Deklarationsliste (VNB ⟶ MGV)\n"),
    "18WT": ("Dateneingang der DZR Stand 15. WT (BIKO ⟵ VNB)\n" "Deklarationsmitteilung (MGV ⟶ BKV)\n"),
    "20WT": ("Ausgleichsenergiepreise (BIKO ⟶ BKV)\n" "Abstimmung NKP zw. VNB\n"),
    "21WT": "NKP (VNB ⟶ MGV)",
    "26WT": "NKP MG-Überlappung (VNB ⟶ MGV)",
    "30WT": "letztmalig Datenannahme zur 1. BK-Abrechnung beim BIKO",
    "42WT": "BK-Abrechnung (BIKO ⟶ BKV)",
    "LWT": "BK-Zuordnungsliste (VNB ⟶ BKV)",
    "3LWT": "Letzter Termin Anmeldung asynchrone Bilanzierung (Strom)",
}
"""
A dictionary with a specific descriptions of the frists

"""

greeting: str = "Digitaler Hochfrequenz Fristenkalender \n"
general_description: str = (
    "\n Um die Kalenderereignisse einfach zu löschen, geben Sie \n"
    "'Hochfrequenz Fristenkalender' in das Suchfeld Ihrer Kalenderapp ein \n"
    "und bearbeiten Sie die Liste nach Wunsch.\n\n"
    "Hochfrequenz Unternehmensberatung GmbH\n"
    "Nördliche Münchner Straße 27A\n"
    "D-82031 Grünwald\n"
    "https://www.hochfrequenz.de/"
)


class FristenkalenderGenerator:
    """
    This class can generate a bdew fristen calendar for a given year

    """

    def generate_frist_description(self, frist_date: date, label: Label) -> str:
        """
        Generates a description of Frist for a given date with a given label
        """
        if label == "LWT":
            wt = "letzter"
        elif label == "3LWT":
            wt = "3. letzter"
        else:
            wt = str(re.findall(r"\d+", label)[0]).strip("'") + "."
        year: str = str(frist_date.year)
        month: str = _month_mapping[frist_date.month]  # Verwendung der Monatszahl statt des Namens
        another_part: str = wt + " Werktag des Fristenmonats " + month + " " + year + " \n"
        frist_description: str = (
            greeting + "\n" + another_part + "\n" + specific_description[label] + "\n" + general_description
        )

        return frist_description

    def generate_fristen_for_type(self, year: int, fristen_type: FristenType) -> list[FristWithAttributesAndType]:
        """
        Generates a list of fristen for a given year with a given type
        """
        fristen: list[FristWithAttributesAndType] = []

        stringified_fristen_type: str = fristen_type.value

        for label in _fristen_type_to_label_mapping[stringified_fristen_type]:
            if label == "LWT":
                nth_day = 0
            elif label == "3LWT":
                nth_day = 3
            elif "LWT" in label:
                raise NotImplementedError("Only LWT and 3LWT are implemented at the moment")
            else:
                nth_day = int(re.findall(r"\d+", label)[0])
            days_and_labels = [(nth_day, label)]
            fristen_with_attributes = self.generate_specific_fristen(year, days_and_labels)
            for frist in fristen_with_attributes:
                frist_with_attributes_and_type = FristWithAttributesAndType(
                    date=frist.date,
                    label=frist.label,
                    ref_not_in_the_same_month=frist.ref_not_in_the_same_month,
                    description=specific_description[label],
                    fristen_type=fristen_type,
                )
                fristen.append(frist_with_attributes_and_type)

        return fristen

    def generate_all_fristen_for_given_wt(self, year: int, nth_day: int, label: Label) -> list[FristWithAttributes]:
        """
        Generate the list of fristen for a given year that are on the nth WT (Werktag) of each month of the calendar
        """

        fristen: list[FristWithAttributes] = []

        # some fristen starting in Oct/Nov/Dec of the previous year might be relevant
        # we first add them all to the result list and later on remove those entries
        # that are not relevant

        # oct, nov and dec from last year

        for month in range(10, 13):
            nth_working_day_of_month_date = get_nth_working_day_of_month(nth_day, start=date(year - 1, month, 1))
            if nth_working_day_of_month_date.month != month:
                ref_not_in_the_same_month = month - 1
            else:
                ref_not_in_the_same_month = None

            fristen.append(
                FristWithAttributes(
                    nth_working_day_of_month_date, label, ref_not_in_the_same_month, specific_description[label]
                )
            )

        # this year
        n_months = 12
        for i_month in range(1, n_months + 1):
            nth_working_day_of_month_date = get_nth_working_day_of_month(nth_day, start=date(year, i_month, 1))
            if nth_working_day_of_month_date.month != i_month:
                ref_not_in_the_same_month = i_month - 1
                if ref_not_in_the_same_month < 1:
                    ref_not_in_the_same_month += 12
            else:
                ref_not_in_the_same_month = None
            fristen.append(
                FristWithAttributes(
                    nth_working_day_of_month_date, label, ref_not_in_the_same_month, specific_description[label]
                )
            )

        # jan of next year
        nth_working_day_of_month_date = get_nth_working_day_of_month(nth_day, start=date(year + 1, 1, 1))
        if nth_working_day_of_month_date.month != 1:
            ref_not_in_the_same_month = 11
        else:
            ref_not_in_the_same_month = None
        fristen.append(
            FristWithAttributes(
                nth_working_day_of_month_date, label, ref_not_in_the_same_month, specific_description[label]
            )
        )

        # the Hochfrequenz Fristenkalender ranges from December of the previous year
        # until the end of January of the following year
        lower_bound = date(year - 1, 12, 1)
        upper_bound = date(year + 1, 2, 1)
        fristen_filtered = [frist for frist in fristen if lower_bound <= frist.date < upper_bound]

        return fristen_filtered

    def _generate_lwt_frist(self, year: int, month: int, nth_day: int, label: LwtLabel) -> FristWithAttributes:
        """
        Generate a frist with a given last working day.
        The last day in the month is counted irrespective if it's a working day or not.
        """
        # pylint:disable=line-too-long
        # Discussion 2024-12-06; https://teams.microsoft.com/l/message/19:e8371dfe0911491dab42b1c9e38d82e4@thread.v2/1733479374344?context=%7B%22contextType%22%3A%22chat%22%7D
        # Quote Joscha:
        # Der Abstand muss 3 Werktage umfassen. Also sprich der 3. Werktag vor dem Monatsletzten ist "3LWT".
        # Der Monatsletzte selbst wird nicht mitgezählt.
        # Um Deine beiden Beispiele Mai 2022 und Oktober 2022 aufzugreifen.
        # Mai:
        # - Monatsletzter ist der 31.05. -> 30.05. = 1 LWT,
        # - 27.05. = 2 LWT
        # - 25.05. = 3 LWT (26.5. wird nicht gezählt da Feiertag)
        # Oktober:
        # - Monatsletzter ist der 31.10. -> 28.10. = 1 LWT
        # - 27.10. = 2 LWT
        # - 26.10. = 3 LWT
        last_day_of_month = monthrange(year, month)[1]
        last_date_of_month = date(year, month, last_day_of_month)
        _0lwt = last_date_of_month
        if nth_day == 0:
            first_date_of_next_month = last_date_of_month + timedelta(days=1)
            result = get_previous_working_day(first_date_of_next_month)
        else:
            result = _0lwt
            for _ in range(nth_day):  # each iteration 0LWT => 1LWT => 2LWT => 3LWT ...
                result = get_previous_working_day(result)
        return FristWithAttributes(result, label, None, specific_description[label])

    def generate_all_fristen_for_given_lwt(self, year: int, nth_day: int, label: LwtLabel) -> list[FristWithAttributes]:
        """
        Generate the list of fristen for a given year that are on the nth LWT (letzter Werktag, last working day)
        of each month of the calendar.
        LWT are counted back into the month starting from the last day of the month.
        The last day of the month is counted irrespective if it is a Werktag or not.
        """

        fristen: list[FristWithAttributes] = []

        # dez last year
        fristen.append(self._generate_lwt_frist(year - 1, 12, nth_day, label))

        # this year
        n_months = 12
        for i_month in range(1, n_months + 1):
            fristen.append(self._generate_lwt_frist(year, i_month, nth_day, label))

        # jan next year
        fristen.append(self._generate_lwt_frist(year + 1, 1, nth_day, label))
        # 3LWT originates from the "asynchrone Bilanzierung" which ends with the beginning of 24h Lieferantenwechsel
        # hence we don't need those kind of fristen afterward.
        fristen_without_3lwt_after_24h_lfw = [
            f for f in fristen if not (f.label == "3LWT" and f.date >= _24hLfwKeyDate)
        ]
        return fristen_without_3lwt_after_24h_lfw

    def generate_all_fristen(self, year: int) -> list[FristWithAttributes]:
        """
        Generate the list of all Fristen in the calendar for a given year
        """
        days_and_labels = list(_DAYS_AND_LABELS.items())
        fristen = self.generate_specific_fristen(year, days_and_labels)
        fristen.sort(key=lambda fwa: fwa.date)
        return fristen

    def generate_specific_fristen(
        self, year: int, days_and_labels: list[tuple[int, Label]]
    ) -> list[FristWithAttributes]:
        """
        Generate the list of Fristen in the calendar for a given year for a given set of Fristen
        The specification of the Fristen is for example: days_and_labels = [(5, '5WT'), (3, 'LWT), ...]
        The only two valid format for the label string is an integer followed by one of the two endings:
        WT (Werktag) or LWT (letzter Werktag)
        """

        fristen = []
        for days, label in days_and_labels:
            if label == "LWT" or label == "3LWT":  # pylint:disable=consider-using-in
                # ignore pylint because we need the x==FOO or x==BAR for mypy LwtLabel type
                fristen += self.generate_all_fristen_for_given_lwt(year, days, label)
            elif label.endswith("WT"):
                fristen += self.generate_all_fristen_for_given_wt(year, days, label)
            else:
                raise ValueError(f"The label '{label}' must end with either 'WT' or 'LWT'")

        fristen.sort(key=lambda fwa: fwa.date)
        return fristen

    def create_ical_event(self, frist: Union[FristWithAttributes, FristWithAttributesAndType]) -> Event:
        """
        Create an ical (v)event for a given frist
        """
        event = Event()
        summary: str = frist.label
        if frist.ref_not_in_the_same_month is not None:
            summary += f" (⭐{frist.ref_not_in_the_same_month})"
        event.add("summary", summary)
        event.add("description", self.generate_frist_description(frist.date, frist.label))
        event.add("dtstart", frist.date)
        event.add("transp", "TRANSPARENT")
        if sys.version_info >= (3, 11):
            event.add("dtstamp", datetime.now(UTC))
        else:
            event.add("dtstamp", datetime.utcnow())

        # UID: YYYYMMDD<type><label><date>
        creation_date = datetime.now().strftime("%Y%m%d")
        frist_type_attr = getattr(frist, "frist_type", None)
        frist_type = frist_type_attr.value if isinstance(frist_type_attr, FristenType) else "ALL"
        frist_date = frist.date.strftime("%Y%m")
        label_clean = frist.label.replace("WT", "").replace("L", "L0")
        uid = f"{creation_date}{frist_type}{label_clean}{frist_date}"
        event.add("uid", uid)

        event.add("categories", frist.label)
        # pylint:disable=line-too-long
        # https://learn.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxcical/1c64465c-7d88-4b0f-988f-6e40a289c57f
        # Note that categories is not part of the official ICAL standard but microsoft specific.

        return event

    def create_ical(
        self, attendee: str, fristen: list[Union[FristWithAttributes, FristWithAttributesAndType]]
    ) -> Calendar:
        """
        Create an ical calendar with a given mail address and a given set of fristen
        """
        calendar = Calendar()
        calendar.add("attendee", attendee)
        calendar.add("x-wr-calname", "Hochfrequenz Fristenkalender")
        # https://learn.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxcical/1da58449-b97e-46bd-b018-a1ce576f3e6d

        for frist in fristen:
            calendar.add_component(self.create_ical_event(frist))

        return calendar

    def export_ical(self, file_path: Path, cal: Calendar) -> None:
        """
        Write .ics file from calendar
        """
        with open(file_path, "wb") as file:
            file.write(cal.to_ical())

    def generate_and_export_fristen_for_type(
        self, file_path: Path, attendee: str, year: int, fristen_type: FristenType
    ) -> None:
        """
        Generates fristen for a given type and exports it to an .ics file
        """
        fristen_for_type = self.generate_fristen_for_type(year, fristen_type)
        calendar = self.create_ical(attendee, fristen_for_type)  # type: ignore[arg-type]
        self.export_ical(file_path, calendar)

    def generate_and_export_whole_calendar(self, file_path: Path, attendee: str, year: int) -> None:
        """
        Generates a calendar for a given year and exports it to an .ics file
        """
        all_fristen = self.generate_all_fristen(year)
        calendar = self.create_ical(attendee, all_fristen)
        self.export_ical(file_path, calendar)
