# card_drills.py
import streamlit as st
from mnemonica import (
    render_manual as mn_render_manual,
    render_auto as mn_render_auto,
    render_flashcards as mn_render_flashcards,  # NEW
)

st.set_page_config(
    page_title="Stack Trainer",
    page_icon="🃏",
    layout="centered",
)

ss = st.session_state
if "page" not in ss:
    ss.page = "info"  # 'info', 'mn_manual', 'mn_auto', 'mn_flash'


def show_info():
    st.title("📘 Information")
    st.markdown(
        """
This app helps you train **memorized deck stacks**.

Currently included:

- 🧠 **Mnemonica** by Juan Tamariz  

Modes:

- **Manual drills** – you click *New question* when ready.  
- **Auto drills** – timed, hands-free practice with *Start / Stop / New session*.  
- **Mixed drills** – combines both directions (Number ↔ Card) randomly.  
- **Flashcards** – visual, flip-style practice with no typing.
"""
    )


# =============== SIDEBAR NAVBAR ===============
with st.sidebar:
    st.title("🃏 Stack Trainer")

    # Top-level buttons
    if st.button("Information"):
        ss.page = "info"

    with st.expander("Mnemonica", expanded=ss.page.startswith("mn_")):
        if st.button("Flashcards"):               # NEW
            ss.page = "mn_flash"
        if st.button("Manual drills"):
            ss.page = "mn_manual"
        if st.button("Auto drills"):
            ss.page = "mn_auto"
    st.markdown("---")
    st.caption("More stacks are about to come...")


# =============== ROUTING ===============
if ss.page == "info":
    show_info()
elif ss.page == "mn_manual":
    mn_render_manual()
elif ss.page == "mn_auto":
    mn_render_auto()
elif ss.page == "mn_flash":           # NEW
    mn_render_flashcards()
