import calendar
import json
import os
from datetime import date, time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="FamCalendar", layout="wide")

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

API_BASE_URL = os.environ.get("FAMCALENDAR_API_URL", "http://localhost:8000")
CATEGORIES = ["Familie", "Skole", "Sundhed", "Hverdag", "Fritid"]


@st.cache_data(ttl=10)
def load_appointments() -> pd.DataFrame:
    request = Request(f"{API_BASE_URL}/appointments")

    with urlopen(request, timeout=3) as response:
        appointments = json.load(response)

    df = pd.DataFrame(appointments)

    if df.empty:
        empty_df = pd.DataFrame(
            columns=["id", "dato", "tid", "aftale", "kategori", "maaned", "ugedag"]
        )
        empty_df["dato"] = pd.to_datetime(empty_df["dato"])
        return empty_df

    df["dato"] = pd.to_datetime(df["dato"])
    df["maaned"] = df["dato"].dt.month.map(MONTHS_DA)
    df["ugedag"] = df["dato"].dt.day_name()
    return df


def create_appointment(dato: date, tid: str, aftale: str, kategori: str) -> None:
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


def create_appointment_with_ai(message: str) -> None:
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
    # Henter de faerdige NumPy-resultater fra backend'en.
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
    # Rydder cache, saa nye eller slettede aftaler ogsaa slaar igennem i analysen.
    load_appointments.clear()
    load_numpy_analysis.clear()
    st.rerun()


def change_page(page_name: str) -> None:
    st.session_state["next_page"] = page_name


def render_add_appointment_form(appointment_date: date) -> None:
    with st.form(f"appointment_form_{appointment_date.isoformat()}", clear_on_submit=True):
        appointment_time = st.time_input("Tid", value=time(12, 0))
        title = st.text_input("Aftale")
        category = st.selectbox("Kategori", CATEGORIES)
        submitted = st.form_submit_button("Gem aftale")

    if submitted:
        if not title.strip():
            st.error("Skriv en aftale før du gemmer.")
            return

        try:
            create_appointment(
                dato=appointment_date,
                tid=appointment_time.strftime("%H:%M"),
                aftale=title.strip(),
                kategori=category,
            )
        except (HTTPError, URLError) as error:
            st.error(f"Aftalen kunne ikke gemmes: {error}")
            return

        st.session_state["add_appointment_date"] = None
        st.session_state["last_saved_message"] = "Aftalen er gemt og vises i Dataframe."
        change_page("Dataframe")
        refresh_appointments()


def render_ai_assistant() -> None:
    st.header("AI-assistent")
    st.write("Skriv en aftale med almindelig tekst, så opretter assistenten den i kalenderen.")

    with st.form("ai_appointment_form", clear_on_submit=True):
        message = st.text_area(
            "Hvad skal oprettes?",
            placeholder=(
                "Fx: Tilføj tandlæge på fredag kl. 10\n"
                "Fx: Opret fodboldtræning den 20. maj kl. 17"
            ),
            height=140,
        )
        submitted = st.form_submit_button("Opret med AI")

    if submitted:
        if not message.strip():
            st.error("Skriv en besked til AI-assistenten først.")
            return

        try:
            create_appointment_with_ai(message.strip())
        except HTTPError as error:
            try:
                detail = json.loads(error.read().decode("utf-8")).get(
                    "detail",
                    str(error),
                )
            except json.JSONDecodeError:
                detail = str(error)
            st.error(f"AI-assistenten kunne ikke oprette aftalen: {detail}")
            return
        except URLError as error:
            st.error(f"AI-assistenten kunne ikke kontakte backend'en: {error}")
            return

        st.session_state["last_saved_message"] = "AI-assistenten har oprettet aftalen."
        change_page("Dataframe")
        refresh_appointments()


def render_calendar(df: pd.DataFrame) -> None:
    selected_month_name = st.sidebar.selectbox(
        "Vælg måned",
        list(MONTHS_DA.values()),
        index=date.today().month - 1,
    )
    selected_month = list(MONTHS_DA.keys())[
        list(MONTHS_DA.values()).index(selected_month_name)
    ]
    month_df = df[df["dato"].dt.month == selected_month]

    st.header(f"{selected_month_name} {YEAR}")

    days_in_month = calendar.monthrange(YEAR, selected_month)[1]
    add_appointment_date = st.session_state.get("add_appointment_date")

    for day in range(1, days_in_month + 1):
        current_date = date(YEAR, selected_month, day)
        day_appointments = month_df[month_df["dato"].dt.date == current_date]

        with st.container(border=True):
            st.subheader(current_date.strftime("%d/%m/%Y"))

            if day_appointments.empty:
                st.write("Ingen aftaler")
            else:
                for appointment in day_appointments.itertuples():
                    details, delete_button = st.columns([5, 1])

                    with details:
                        st.write(
                            f"{appointment.tid} - {appointment.aftale} "
                            f"({appointment.kategori})"
                        )

                    with delete_button:
                        if st.button("Slet", key=f"delete_{appointment.id}"):
                            try:
                                delete_appointment(int(appointment.id))
                            except (HTTPError, URLError) as error:
                                st.error(f"Aftalen kunne ikke slettes: {error}")
                                return

                            st.success("Aftalen er slettet.")
                            refresh_appointments()

            if st.button("Tilføj aftale", key=f"add_{current_date.isoformat()}"):
                st.session_state["add_appointment_date"] = current_date.isoformat()
                st.rerun()

            if add_appointment_date == current_date.isoformat():
                render_add_appointment_form(current_date)


def render_dataframe(df: pd.DataFrame) -> None:
    st.header("Aftaler som Pandas dataframe")

    if st.session_state.get("last_saved_message"):
        st.success(st.session_state.pop("last_saved_message"))

    if st.button("Opdater dataframe"):
        refresh_appointments()

    st.dataframe(
        df.sort_values("dato"),
        width="stretch",
        hide_index=True,
    )


def render_chart(df: pd.DataFrame) -> None:
    st.header("Travleste maaneder")

    if df.empty:
        st.info("Der er ingen aftaler at vise endnu.")
        return

    appointments_per_month = (
        df.groupby("maaned")
        .size()
        .reindex(MONTHS_DA.values(), fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(appointments_per_month.index, appointments_per_month.values, color="#2E86AB")
    ax.set_xlabel("Maaned")
    ax.set_ylabel("Antal aftaler")
    ax.set_title("Antal aftaler pr. maaned")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    st.pyplot(fig)


def render_count_results(title: str, results: list[dict]) -> None:
    # Viser en lille liste med de mest brugte tider, dage eller datoer.
    st.subheader(title)

    if not results:
        st.write("Ingen data endnu.")
        return

    for result in results:
        st.write(f"{result['label']}: {result['count']} aftaler")


def render_numpy_analysis() -> None:
    st.header("AI + NumPy analyse")

    try:
        # Frontend'en beregner ikke selv her; den viser svaret fra backend'en.
        analysis = load_numpy_analysis()
    except (HTTPError, URLError) as error:
        st.error(f"NumPy-analysen kunne ikke hentes: {error}")
        return

    if analysis["total_appointments"] == 0:
        st.info("Der er ingen aftaler at analysere endnu.")
        return

    st.metric("Aftaler analyseret", analysis["total_appointments"])

    # Deler resultaterne i to kolonner, saa overblikket er lettere at laese.
    col1, col2 = st.columns(2)
    with col1:
        render_count_results("Tidspunkter der bruges mest", analysis["most_used_times"])
        render_count_results("Mest aktive ugedage", analysis["most_active_weekdays"])

    with col2:
        render_count_results("Mest fyldte datoer", analysis["busiest_dates"])
        render_count_results("Mest aktive timer", analysis["most_active_hours"])


st.title("FamCalendar")

try:
    appointments_df = load_appointments()
except URLError:
    st.error(
        "Backend'en kører ikke endnu. Start den med: "
        "`uv run uvicorn FamCalender.backend.main:app --reload --port 8000`"
    )
    st.stop()

if st.session_state.get("next_page"):
    st.session_state["page"] = st.session_state.pop("next_page")

page = st.sidebar.selectbox(
    "Navigation",
    ["Kalender", "AI-assistent", "Dataframe", "Matplotlib chart", "NumPy analyse"],
    key="page",
)

if page == "Kalender":
    render_calendar(appointments_df)
elif page == "AI-assistent":
    render_ai_assistant()
elif page == "Dataframe":
    render_dataframe(appointments_df)
elif page == "Matplotlib chart":
    render_chart(appointments_df)
else:
    render_numpy_analysis()
