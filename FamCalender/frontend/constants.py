import os


YEAR = 2026

MONTHS_DA = {
    1: "Januar",
    2: "Februar",
    3: "Marts",
    4: "April",
    5: "Maj",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "December",
}

WEEKDAYS_DA = {
    0: "Mandag",
    1: "Tirsdag",
    2: "Onsdag",
    3: "Torsdag",
    4: "Fredag",
    5: "Lørdag",
    6: "Søndag",
}

API_BASE_URL = os.environ.get("FAMCALENDAR_API_URL", "http://localhost:8000")
CATEGORIES = ["Familie", "Skole", "Sundhed", "Hverdag", "Fritid"]
