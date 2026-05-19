import json
from datetime import date, time
from urllib.error import HTTPError, URLError

import pandas as pd
import streamlit as st

from FamCalender.frontend.api import (
    create_appointment,
    create_appointment_with_ai,
    refresh_appointments,
    update_appointment,
)
from FamCalender.frontend.constants import CATEGORIES
from FamCalender.frontend.navigation import change_page


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
        # Efter gemning sendes brugeren til dataframe-siden, hvor den nye aftale ses.
        change_page("Dataframe")
        refresh_appointments()


def render_edit_appointment_form(appointment: pd.Series) -> None:
    appointment_id = int(appointment.id)

    with st.form(f"edit_appointment_form_{appointment_id}"):
        appointment_date = st.date_input("Dato", value=appointment.dato.date())
        appointment_time = st.time_input(
            "Tid",
            value=time.fromisoformat(appointment.tid),
        )
        title = st.text_input("Aftale", value=appointment.aftale)
        category = st.selectbox(
            "Kategori",
            CATEGORIES,
            index=CATEGORIES.index(appointment.kategori)
            if appointment.kategori in CATEGORIES
            else 0,
        )
        save_button, cancel_button = st.columns(2)
        with save_button:
            submitted = st.form_submit_button("Gem ændringer")
        with cancel_button:
            cancelled = st.form_submit_button("Annuller")

    if cancelled:
        st.session_state["edit_appointment_id"] = None
        st.rerun()

    if submitted:
        if not title.strip():
            st.error("Skriv en aftale før du gemmer.")
            return

        try:
            update_appointment(
                appointment_id=appointment_id,
                dato=appointment_date,
                tid=appointment_time.strftime("%H:%M"),
                aftale=title.strip(),
                kategori=category,
            )
        except (HTTPError, URLError) as error:
            st.error(f"Aftalen kunne ikke opdateres: {error}")
            return

        st.session_state["edit_appointment_id"] = None
        st.session_state["last_saved_message"] = "Aftalen er opdateret."
        refresh_appointments()


def render_ai_assistant() -> None:
    st.header("AI-assistent")
    st.write("Skriv en aftale med almindelig tekst, så opretter assistenten den i kalenderen.")

    with st.form("ai_appointment_form", clear_on_submit=True):
        message = st.text_area(
            "Hvad skal oprettes?",
            placeholder="Fx: Tandlæge på fredag kl. 10",
            height=100,
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

        st.session_state["last_saved_message"] = (
            "Aftalen er oprettet med AI og ligger nu i kalenderen."
        )
        change_page("Dataframe")
        refresh_appointments()
