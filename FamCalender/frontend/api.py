import json
from datetime import date
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st

from FamCalender.frontend.constants import (
    API_BASE_URL,
    MONTHS_DA,
    WEEKDAYS_DA,
)


@st.cache_data(ttl=10)
def load_appointments() -> pd.DataFrame:
    # Cache mindsker antallet af kald til backend'en, mens appen genindlæses.
    request = Request(f"{API_BASE_URL}/appointments")

    with urlopen(request, timeout=3) as response:
        appointments = json.load(response)

    df = pd.DataFrame(appointments)

    if df.empty:
        # Tom dataframe får samme kolonner som en fyldt, så resten af UI'et virker.
        empty_df = pd.DataFrame(
            columns=["id", "dato", "tid", "aftale", "kategori", "måned", "ugedag"]
        )
        empty_df["dato"] = pd.to_datetime(empty_df["dato"])
        return empty_df

    df["dato"] = pd.to_datetime(df["dato"])
    df["måned"] = df["dato"].dt.month.map(MONTHS_DA)
    df["ugedag"] = df["dato"].dt.weekday.map(WEEKDAYS_DA)
    return df


def create_appointment(dato: date, tid: str, aftale: str, kategori: str) -> None:
    # Sender formularens felter til FastAPI som JSON.
    payload = {
        "dato": dato.isoformat(),
        "tid": tid,
        "aftale": aftale,
        "kategori": kategori,
    }
    request = Request(
        f"{API_BASE_URL}/appointments",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=3):
        pass


def update_appointment(
    appointment_id: int,
    dato: date,
    tid: str,
    aftale: str,
    kategori: str,
) -> None:
    payload = {
        "dato": dato.isoformat(),
        "tid": tid,
        "aftale": aftale,
        "kategori": kategori,
    }
    request = Request(
        f"{API_BASE_URL}/appointments/{appointment_id}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PUT",
    )

    with urlopen(request, timeout=3):
        pass


def create_appointment_with_ai(message: str) -> None:
    # Sender brugerens fritekst til backend'en, hvor OpenAI kaldes.
    payload = {"besked": message}
    request = Request(
        f"{API_BASE_URL}/llm/appointments",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=20):
        pass


@st.cache_data(ttl=10)
def load_numpy_analysis() -> dict:
    # Henter de færdige NumPy-resultater fra backend'en.
    request = Request(f"{API_BASE_URL}/analytics/numpy")

    with urlopen(request, timeout=3) as response:
        return json.load(response)


def delete_appointment(appointment_id: int) -> None:
    request = Request(
        f"{API_BASE_URL}/appointments/{appointment_id}",
        method="DELETE",
    )

    with urlopen(request, timeout=3):
        pass


def refresh_appointments() -> None:
    # Rydder cache, så nye, ændrede eller slettede aftaler slår igennem i analysen.
    load_appointments.clear()
    load_numpy_analysis.clear()
    st.rerun()
