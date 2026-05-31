from urllib.error import URLError
from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from FamCalender.frontend.api import load_appointments  # noqa: E402
from FamCalender.frontend.calendar_view import render_calendar  # noqa: E402
from FamCalender.frontend.forms import render_ai_assistant  # noqa: E402
from FamCalender.frontend.matplotlib_view import render_chart  # noqa: E402
from FamCalender.frontend.numpy_analysis_view import render_numpy_analysis  # noqa: E402
from FamCalender.frontend.pandas_view import render_dataframe  # noqa: E402


st.set_page_config(page_title="FamCalendar", layout="wide")
st.title("FamCalendar")

try:
    appointments_df = load_appointments()
except URLError:
    st.error(
        "Backend'en kører ikke endnu. Start applikationen med: `make up`"
    )
    st.stop()

if st.session_state.get("next_page"):
    # next_page bliver sat efter oprettelse, så navigationen følger handlingen.
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
