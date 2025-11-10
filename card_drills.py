# card_drills.py
import streamlit as st
from mnemonica import render_manual as mn_render_manual, render_auto as mn_render_auto

st.set_page_config(
    page_title="Stack Trainer",
    page_icon="🃏",
    layout="centered",
)

ss = st.session_state
if "page" not in ss:
    ss.page = "info"  # 'info', 'mn_manual', 'mn_auto'


def show_info():
    st.title("📘 Information")
    st.markdown(
        """
This app helps you train **memorized deck stacks**.

Currently included:

- 🧠 **Mnemonica** by Juan Tamariz  

Modes:

- **Manual drills** – you click *New question* when ready.
- **Auto drills** – timed practice with **Start / Stop / New session**.

Each stack lives in its own Python file (e.g. `mnemonica.py`, `aronson.py`).
"""
    )


# =============== SIDEBAR NAVBAR ===============
with st.sidebar:
    st.title("🃏 Stack Trainer")

    # Top-level buttons
    if st.button("Information"):
        ss.page = "info"

    with st.expander("Mnemonica", expanded=ss.page.startswith("mn_")):
        if st.button("Manual drills"):
            ss.page = "mn_manual"
        if st.button("Auto drills"):
            ss.page = "mn_auto"

    st.markdown("---")
    st.caption("More stacks (Aronson, Bart Harding, etc.) can be added as new files later.")


# =============== ROUTING ===============
if ss.page == "info":
    show_info()
elif ss.page == "mn_manual":
    mn_render_manual()
elif ss.page == "mn_auto":
    mn_render_auto()
