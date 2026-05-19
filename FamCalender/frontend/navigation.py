import streamlit as st


def change_page(page_name: str) -> None:
    # Streamlit kan ikke skifte selectbox direkte midt i et render, så vi gemmer næste side.
    st.session_state["next_page"] = page_name
