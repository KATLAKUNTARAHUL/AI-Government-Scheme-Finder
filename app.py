from __future__ import annotations

import streamlit as st

from utils.ui import render_chatbot_page, render_dashboard, render_eligibility_page, render_recommendations_page


st.set_page_config(
    page_title="AI Government Scheme Finder",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a section",
        ["Dashboard", "Eligibility", "Recommendations", "Chatbot"],
        label_visibility="collapsed",
    )

    if page == "Dashboard":
        render_dashboard()
    elif page == "Eligibility":
        render_eligibility_page()
    elif page == "Recommendations":
        render_recommendations_page()
    else:
        render_chatbot_page()


if __name__ == "__main__":
    main()