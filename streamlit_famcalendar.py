import streamlit as st
import calendar
from datetime import date

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

st.title("FamCalendar")

selected_month_name = st.sidebar.selectbox(
    "Vælg måned",
    list(MONTHS_DA.values())
)

selected_month = list(MONTHS_DA.keys())[
    list(MONTHS_DA.values()).index(selected_month_name)
]

st.header(f"{selected_month_name} {YEAR}")

days_in_month = calendar.monthrange(YEAR, selected_month)[1]

appointments = {
    "2026-01-05": ["Tandlæge kl. 10:00"],
    "2026-01-12": ["Familieaftale kl. 17:00"],
    "2026-02-03": ["Skole møde kl. 09:00"],
}

for day in range(1, days_in_month + 1):
    current_date = date(YEAR, selected_month, day)
    date_key = current_date.isoformat()

    with st.container(border=True):
        st.subheader(current_date.strftime("%d/%m/%Y"))

        if date_key in appointments:
            for appointment in appointments[date_key]:
                st.write(f"📌 {appointment}")
        else:
            st.write("Ingen aftaler")

        if st.button("Tilføj aftale", key=f"add_{date_key}"):
            st.info(f"Her kan du senere lave formular til {current_date.strftime('%d/%m/%Y')}")