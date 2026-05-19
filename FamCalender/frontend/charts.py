import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from FamCalender.frontend.constants import MONTHS_DA, WEEKDAYS_DA


def render_bar_chart(
    labels: pd.Index,
    values: pd.Series,
    xlabel: str,
    title: str,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, values, color="#2E86AB")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Antal aftaler")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    st.pyplot(fig)


def render_chart(df: pd.DataFrame) -> None:
    st.header("Matplotlib chart")

    if df.empty:
        st.info("Der er ingen aftaler at vise endnu.")
        return

    weekday_tab, month_tab = st.tabs(["Ugedage", "Måneder"])

    appointments_per_weekday = (
        df.groupby("ugedag")
        .size()
        .reindex(WEEKDAYS_DA.values(), fill_value=0)
    )
    appointments_per_month = (
        df.groupby("måned")
        .size()
        .reindex(MONTHS_DA.values(), fill_value=0)
    )

    with weekday_tab:
        render_bar_chart(
            labels=appointments_per_weekday.index,
            values=appointments_per_weekday,
            xlabel="Ugedag",
            title="Antal aftaler pr. ugedag",
        )

    with month_tab:
        render_bar_chart(
            labels=appointments_per_month.index,
            values=appointments_per_month,
            xlabel="Måned",
            title="Antal aftaler pr. måned",
        )
