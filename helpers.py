import time
import streamlit as st

def format_card(card: str) -> str:
    rank = card[:-1]
    suit = card[-1]
    symbol = {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}[suit]
    color = "red" if suit in ["H", "D"] else "black"
    return (
        f"<span style='font-size:2.4rem;"
        f"color:{color};font-weight:700'>{rank}{symbol}</span>"
    )

def normalize_card_input(text: str) -> str:
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
    placeholder = st.empty()
    for i in range(seconds, 0, -1):
        placeholder.markdown(f"⏳ **{label}: {i}**")
        time.sleep(1)
    placeholder.empty()

def rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()
