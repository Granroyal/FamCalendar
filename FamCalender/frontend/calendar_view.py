import calendar
from datetime import date
from urllib.error import HTTPError, URLError

import pandas as pd
import streamlit as st

from FamCalender.frontend.api import delete_appointment, refresh_appointments
from FamCalender.frontend.constants import MONTHS_DA, WEEKDAYS_DA, YEAR
from FamCalender.frontend.forms import (
    render_add_appointment_form,
    render_edit_appointment_form,
)


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
    edit_appointment_id = st.session_state.get("edit_appointment_id")

    for day in range(1, days_in_month + 1):
        current_date = date(YEAR, selected_month, day)
        day_appointments = month_df[month_df["dato"].dt.date == current_date]

        with st.container(border=True):
            weekday_name = WEEKDAYS_DA[current_date.weekday()]
            st.subheader(f"{weekday_name} den {day}. {selected_month_name.lower()}")
            st.caption(current_date.strftime("%d/%m/%Y"))

            if day_appointments.empty:
                st.write("Ingen aftaler")
            else:
                for appointment in day_appointments.sort_values("tid").itertuples():
                    details, edit_button, delete_button = st.columns([5, 1, 1])

                    with details:
                        st.markdown(f"**{appointment.tid}** · {appointment.aftale}")
                        st.caption(appointment.kategori)

                    with edit_button:
                        if st.button("Rediger", key=f"edit_{appointment.id}"):
                            st.session_state["edit_appointment_id"] = int(appointment.id)
                            st.rerun()

                    with delete_button:
                        if st.button("Slet", key=f"delete_{appointment.id}"):
                            try:
                                delete_appointment(int(appointment.id))
                            except (HTTPError, URLError) as error:
                                st.error(f"Aftalen kunne ikke slettes: {error}")
                                return

                            st.success("Aftalen er slettet.")
                            refresh_appointments()

                    if edit_appointment_id == int(appointment.id):
                        render_edit_appointment_form(appointment)

            if st.button("Tilføj aftale", key=f"add_{current_date.isoformat()}"):
                st.session_state["add_appointment_date"] = current_date.isoformat()
                st.rerun()

            if add_appointment_date == current_date.isoformat():
                render_add_appointment_form(current_date)
