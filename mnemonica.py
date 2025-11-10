# mnemonica.py
import random
import streamlit as st

from helpers import format_card, normalize_card_input, countdown, rerun
from stacks import MNEMONICA, MNEMONICA_CARD_TO_POS


# ===================== MANUAL DRILLS =====================
def render_manual():
    ss = st.session_state

    # Per-mode state (manual)
    ss.setdefault("mn_manual_last_position", None)
    ss.setdefault("mn_manual_last_card", None)
    ss.setdefault("mn_manual_num_attempts", 0)
    ss.setdefault("mn_manual_num_correct", 0)
    ss.setdefault("mn_manual_card_attempts", 0)
    ss.setdefault("mn_manual_card_correct", 0)

    st.title("🧠 Mnemonica – Manual drills")

    drill_type = st.selectbox(
        "Drill type",
        ["Number → Card", "Card → Number"],
        key="mn_manual_drill_type",
    )

    st.markdown("Click **New question** whenever you’re ready for the next card/position.")
    st.divider()

    # ---------- NUMBER → CARD ----------
    if drill_type == "Number → Card":
        col1, col2 = st.columns(2)
        with col1:
            start = st.number_input("Start position", 1, 52, 1, key="mn_manual_num_start")
        with col2:
            end = st.number_input("End position", 1, 52, 52, key="mn_manual_num_end")

        if start > end:
            st.error("Start position must be ≤ end position.")
            return

        if st.button("🎲 New question", key="mn_manual_num_new"):
            ss.mn_manual_last_position = random.randint(start, end)
            # safe: before widget instantiation
            ss["mn_manual_num_answer_input"] = ""

        if ss.mn_manual_last_position is not None:
            pos = ss.mn_manual_last_position
            card = MNEMONICA[pos - 1]

            st.markdown(f"### Position: `{pos}`  _(range {start}–{end})_")
            st.info("Say the card at this position, then type it below or reveal it.")

            with st.expander("Reveal card"):
                st.markdown(format_card(card), unsafe_allow_html=True)

            ans = st.text_input(
                "Your answer (e.g. AS, 4C, QH)",
                key="mn_manual_num_answer_input",
            )

            if st.button("Check answer", key="mn_manual_num_check"):
                user = normalize_card_input(ans)
                correct = card
                ss.mn_manual_num_attempts += 1
                if user == correct:
                    ss.mn_manual_num_correct += 1
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. Correct card is: {format_card(card)}")

            # Stats
            attempts = ss.mn_manual_num_attempts
            correct = ss.mn_manual_num_correct
            st.markdown("---")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.metric("Attempts", attempts)
            with col_s2:
                if attempts > 0:
                    pct = (correct / attempts) * 100
                    st.metric("Accuracy", f"{correct}/{attempts}", f"{pct:.0f}%")
                else:
                    st.metric("Accuracy", "–", "+0%")

    # ---------- CARD → NUMBER ----------
    else:
        col1, col2 = st.columns(2)
        with col1:
            card_start = st.number_input(
                "Start position (range)", 1, 52, 1, key="mn_manual_card_start"
            )
        with col2:
            card_end = st.number_input(
                "End position (range)", 1, 52, 52, key="mn_manual_card_end"
            )

        if card_start > card_end:
            st.error("Start position must be ≤ end position.")
            return

        if st.button("🎴 New question", key="mn_manual_card_new"):
            idx = random.randint(card_start - 1, card_end - 1)
            ss.mn_manual_last_card = MNEMONICA[idx]
            ss["mn_manual_card_answer_input"] = ""

        if ss.mn_manual_last_card is not None:
            card = ss.mn_manual_last_card
            pos = MNEMONICA_CARD_TO_POS[card]

            st.markdown("### Current card:")
            st.markdown(format_card(card), unsafe_allow_html=True)
            st.markdown(f"_Range: positions {card_start}–{card_end}_")

            st.info("Say the position in Mnemonica, then type it below or reveal it.")

            with st.expander("Reveal position"):
                st.markdown(f"**Position:** `{pos}`")

            ans_num = st.text_input(
                "Your answer (position 1–52)",
                key="mn_manual_card_answer_input",
            )

            if st.button("Check position", key="mn_manual_card_check"):
                try:
                    user_pos = int(ans_num.strip())
                except (ValueError, AttributeError):
                    user_pos = None

                ss.mn_manual_card_attempts += 1
                if user_pos == pos:
                    ss.mn_manual_card_correct += 1
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. Correct position is: `{pos}`")

            # Stats
            attempts_c = ss.mn_manual_card_attempts
            correct_c = ss.mn_manual_card_correct
            st.markdown("---")
            col_cs1, col_cs2 = st.columns(2)
            with col_cs1:
                st.metric("Attempts", attempts_c)
            with col_cs2:
                if attempts_c > 0:
                    pct_c = (correct_c / attempts_c) * 100
                    st.metric(
                        "Accuracy",
                        f"{correct_c}/{attempts_c}",
                        f"{pct_c:.0f}%",
                    )
                else:
                    st.metric("Accuracy", "–", "+0%")

    st.markdown("---")
    _stack_view()


# ===================== AUTO DRILLS (NO USER INPUT) =====================
def render_auto():
    ss = st.session_state

    # Auto state
    ss.setdefault("mn_auto_num_running", False)
    ss.setdefault("mn_auto_card_running", False)
    ss.setdefault("mn_auto_num_interval", 5)
    ss.setdefault("mn_auto_card_interval", 5)
    ss.setdefault("mn_auto_num_rounds", 0)
    ss.setdefault("mn_auto_card_rounds", 0)

    st.title("🧠 Mnemonica – Auto drills (think only)")

    drill_type = st.selectbox(
        "Drill type",
        ["Number → Card", "Card → Number"],
        key="mn_auto_drill_type",
    )

    st.markdown(
        "In this auto mode, you **never type**:\n\n"
        "1. A question appears.\n"
        "2. You get a countdown (your chosen interval) to **think of the answer**.\n"
        "3. The app then shows the **correct answer**.\n"
        "4. Optional short pause, then the **next question** starts automatically.\n"
    )
    st.divider()

    if drill_type == "Number → Card":
        _auto_number_to_card(ss)
    else:
        _auto_card_to_number(ss)

    st.markdown("---")
    _stack_view()


# ---------- AUTO: NUMBER → CARD (think only) ----------
def _auto_number_to_card(ss):
    col1, col2 = st.columns(2)
    with col1:
        start = st.number_input(
            "Start position", 1, 52, 1, key="mn_auto_num_start"
        )
    with col2:
        end = st.number_input(
            "End position", 1, 52, 52, key="mn_auto_num_end"
        )

    if start > end:
        st.error("Start position must be ≤ end position.")
        return

    ss.mn_auto_num_interval = st.number_input(
        "Thinking time (seconds)",
        min_value=1,
        max_value=60,
        value=ss.mn_auto_num_interval,
        key="mn_auto_num_interval_input",
    )

    colc1, colc2, colc3 = st.columns(3)
    with colc1:
        if st.button("▶ Start session", key="mn_auto_num_start_btn"):
            ss.mn_auto_num_running = True
            rerun()
    with colc2:
        if st.button("⏹ Stop session", key="mn_auto_num_stop_btn"):
            ss.mn_auto_num_running = False
            rerun()
    with colc3:
        if st.button("🔄 Reset counter", key="mn_auto_num_reset_btn"):
            ss.mn_auto_num_rounds = 0
            rerun()

    st.markdown(
        f"**Status:** {'🟢 Running' if ss.mn_auto_num_running else '🔴 Stopped'}  "
        f"• Thinking time: `{ss.mn_auto_num_interval}` seconds"
    )

    if not ss.mn_auto_num_running:
        return

    # One full cycle per run:
    #  1. pick a position
    #  2. show it, countdown
    #  3. show correct card
    #  4. short pause
    #  5. rerun → next question

    pos = random.randint(start, end)
    card = MNEMONICA[pos - 1]
    ss.mn_auto_num_rounds += 1

    st.markdown(f"### Position: `{pos}`  _(range {start}–{end})_")
    st.caption(f"Auto questions this session: `{ss.mn_auto_num_rounds}`")

    st.info("Look at the position and **think of the card**.")

    # Thinking countdown
    countdown(ss.mn_auto_num_interval, label="Think for")

    # Reveal correct answer
    st.success("✅ Time! The card at this position is:")
    st.markdown(format_card(card), unsafe_allow_html=True)

    # Short pause before next
    countdown(3, label="Next position in")

    # Trigger next question
    rerun()


# ---------- AUTO: CARD → NUMBER (think only) ----------
def _auto_card_to_number(ss):
    col1, col2 = st.columns(2)
    with col1:
        card_start = st.number_input(
            "Start position (range)", 1, 52, 1, key="mn_auto_card_start"
        )
    with col2:
        card_end = st.number_input(
            "End position (range)", 1, 52, 52, key="mn_auto_card_end"
        )

    if card_start > card_end:
        st.error("Start position must be ≤ end position.")
        return

    ss.mn_auto_card_interval = st.number_input(
        "Thinking time (seconds)",
        min_value=1,
        max_value=60,
        value=ss.mn_auto_card_interval,
        key="mn_auto_card_interval_input",
    )

    colc1, colc2, colc3 = st.columns(3)
    with colc1:
        if st.button("▶ Start session", key="mn_auto_card_start_btn"):
            ss.mn_auto_card_running = True
            rerun()
    with colc2:
        if st.button("⏹ Stop session", key="mn_auto_card_stop_btn"):
            ss.mn_auto_card_running = False
            rerun()
    with colc3:
        if st.button("🔄 Reset counter", key="mn_auto_card_reset_btn"):
            ss.mn_auto_card_rounds = 0
            rerun()

    st.markdown(
        f"**Status:** {'🟢 Running' if ss.mn_auto_card_running else '🔴 Stopped'}  "
        f"• Thinking time: `{ss.mn_auto_card_interval}` seconds"
    )

    if not ss.mn_auto_card_running:
        return

    # One cycle: pick card, show, countdown, reveal position, pause, rerun
    idx = random.randint(card_start - 1, card_end - 1)
    card = MNEMONICA[idx]
    pos = MNEMONICA_CARD_TO_POS[card]
    ss.mn_auto_card_rounds += 1

    st.markdown("### Current card:")
    st.markdown(format_card(card), unsafe_allow_html=True)
    st.markdown(f"_Range: positions {card_start}–{card_end}_")
    st.caption(f"Auto questions this session: `{ss.mn_auto_card_rounds}`")

    st.info("Look at the card and **think of its Mnemonica position**.")

    countdown(ss.mn_auto_card_interval, label="Think for")

    st.success("✅ Time! The position of this card is:")
    st.markdown(f"**Position:** `{pos}`")

    countdown(3, label="Next card in")

    rerun()


# ===================== STACK VIEW =====================
def _stack_view():
    with st.expander("📜 Show full Mnemonica stack"):
        st.write("Top of deck = position 1")
        for i, card in enumerate(MNEMONICA, start=1):
            st.markdown(f"{i:2d}: {format_card(card)}", unsafe_allow_html=True)
