from urllib.error import HTTPError, URLError

import streamlit as st

from FamCalender.frontend.api import load_numpy_analysis


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

    # Deler resultaterne i to kolonner, så overblikket er lettere at læse.
    col1, col2 = st.columns(2)
    with col1:
        render_count_results("Tidspunkter der bruges mest", analysis["most_used_times"])
        render_count_results("Mest aktive ugedage", analysis["most_active_weekdays"])

    with col2:
        render_count_results("Mest fyldte datoer", analysis["busiest_dates"])
        render_count_results("Mest aktive timer", analysis["most_active_hours"])
