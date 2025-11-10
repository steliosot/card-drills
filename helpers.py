# helpers.py
import time
import streamlit as st


def format_card(card: str) -> str:
    """HTML for card with correct symbol & color."""
    rank = card[:-1]
    suit = card[-1]
    symbol = {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}[suit]
    color = "red" if suit in ["H", "D"] else "black"
    return (
        f"<span style='font-size:2.4rem;"
        f"color:{color};font-weight:700'>{rank}{symbol}</span>"
    )


def normalize_card_input(text: str) -> str:
    """
    Normalize card input like 'as', 'A S', 'A♠', 'a s' -> 'AS'
    Only supports ranks A,2-10,J,Q,K and suits S,H,D,C.
    """
    if not text:
        return ""
    t = text.strip().upper().replace(" ", "")
    t = (
        t.replace("♠", "S")
         .replace("♥", "H")
         .replace("♦", "D")
         .replace("♣", "C")
    )
    return t


def countdown(seconds: int, label: str):
    """
    Blocking countdown: 7, 6, 5...
    Used in Auto drills *after* checking the answer.
    """
    placeholder = st.empty()
    for i in range(seconds, 0, -1):
        placeholder.markdown(f"⏳ **{label}: {i} seconds…**")
        time.sleep(1)
    placeholder.empty()


def rerun():
    """Safe rerun for both new and older Streamlit versions."""
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()
