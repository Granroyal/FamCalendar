import pandas as pd
import streamlit as st

from FamCalender.frontend.api import refresh_appointments


def render_dataframe(df: pd.DataFrame) -> None:
    st.header("Aftaler som Pandas dataframe")

    if st.session_state.get("last_saved_message"):
        st.success(st.session_state.pop("last_saved_message"))

    if st.button("Opdater dataframe"):
        refresh_appointments()

    # Pandas dataframe bruges til at vise de rådata, som backend'en har gemt.
    st.dataframe(
        df.sort_values("dato"),
        width="stretch",
        hide_index=True,
    )
