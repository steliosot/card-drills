# card_drills.py
import streamlit as st
# from mnemonica import (
#     render_manual as mn_render_manual,
#     render_auto as mn_render_auto,
#     render_flashcards as mn_render_flashcards,  # NEW
# )


# mnemonica.py
import random
import streamlit as st

from helpers import format_card, normalize_card_input, countdown, rerun
from stacks import MNEMONICA, MNEMONICA_CARD_TO_POS

def _render_flip_card(question_html: str, answer_html: str,
                      question_label: str, answer_label: str, card_id: str = "mn_flash"):
    """
    Render a CSS flip card: front = question, back = answer.
    Click to flip. Pure HTML+CSS (no JS), using a hidden checkbox.
    """
    html = f"""
<style>
.flip-wrapper-{card_id} {{
  display: flex;
  justify-content: center;
  margin: 1.5rem 0;
}}
.flip-container-{card_id} {{
  perspective: 1200px;
  cursor: pointer;
}}
.flip-checkbox-{card_id} {{
  display: none;
}}
.flip-card-{card_id} {{
  position: relative;
  width: 220px;
  height: 300px;
  transform-style: preserve-3d;
  transition: transform 0.6s ease;
}}
.flip-checkbox-{card_id}:checked + .flip-card-{card_id} {{
  transform: rotateY(180deg);
}}
.flip-face-{card_id} {{
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
  border: 2px solid #e0e0e0;
  box-shadow: 0 6px 16px rgba(0,0,0,0.18);
  background: linear-gradient(135deg,#ffffff,#f7f7f7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
}}
.flip-front-{card_id} {{
}}
.flip-back-{card_id} {{
  transform: rotateY(180deg);
}}
.flip-label-{card_id} {{
  display: inline-block;
}}
.flip-title-{card_id} {{
  font-size: 0.8rem;
  color: #777;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}}
.flip-content-{card_id} {{
  font-size: 2.4rem;
  line-height: 1.1;
}}
</style>

<div class="flip-wrapper-{card_id}">
  <label class="flip-container-{card_id} flip-label-{card_id}">
    <input type="checkbox" class="flip-checkbox-{card_id}">
    <div class="flip-card-{card_id}">
      <!-- Front: question -->
      <div class="flip-face-{card_id} flip-front-{card_id}">
        <div class="flip-title-{card_id}">{question_label}</div>
        <div class="flip-content-{card_id}">
          {question_html}
        </div>
      </div>
      <!-- Back: answer -->
      <div class="flip-face-{card_id} flip-back-{card_id}">
        <div class="flip-title-{card_id}">{answer_label}</div>
        <div class="flip-content-{card_id}">
          {answer_html}
        </div>
      </div>
    </div>
  </label>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

# ---------- VISUAL CARD HELPERS (for flashcards) ----------
def _render_card_box(content_html: str, title: str | None = None):
    """
    Renders a playing-card style box with optional title and inner HTML content.
    """
    title_html = (
        f"<div style='font-size:0.8rem;color:#666;margin-bottom:0.25rem;'>{title}</div>"
        if title
        else ""
    )
    html = f"""
    <div style="
        display:inline-block;
        padding:1.5rem 2rem;
        border-radius:0.9rem;
        border:2px solid #e0e0e0;
        background:linear-gradient(135deg,#ffffff,#f7f7f7);
        box-shadow:0 6px 16px rgba(0,0,0,0.15);
        text-align:center;
        min-width:150px;
    ">
        {title_html}
        <div style="font-size:2.7rem;line-height:1;">
            {content_html}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def _render_position_card(position: int):
    """
    Render a big number styled as a 'position card'.
    """
    html = f"<span style='font-weight:700;color:#333;'>{position}</span>"
    _render_card_box(html, title="Position")

# ===================== MANUAL DRILLS =====================
def mn_render_manual():
    ss = st.session_state

    # Per-mode state (manual)
    ss.setdefault("mn_manual_last_position", None)
    ss.setdefault("mn_manual_last_card", None)
    ss.setdefault("mn_manual_num_attempts", 0)
    ss.setdefault("mn_manual_num_correct", 0)
    ss.setdefault("mn_manual_card_attempts", 0)
    ss.setdefault("mn_manual_card_correct", 0)

    # Mixed manual state
    ss.setdefault("mn_manual_mixed_mode", None)  # "num_to_card" / "card_to_num"
    ss.setdefault("mn_manual_mixed_pos", None)
    ss.setdefault("mn_manual_mixed_card", None)
    ss.setdefault("mn_manual_mixed_attempts", 0)
    ss.setdefault("mn_manual_mixed_correct", 0)

    st.title("🧠 Mnemonica – Manual drills")

    drill_type = st.selectbox(
        "Drill type",
        ["Number → Card", "Card → Number", "Mixed"],
        key="mn_manual_drill_type",
    )

    st.markdown("Click **New question** whenever you’re ready for the next drill.")
    st.divider()

    if drill_type == "Number → Card":
        _manual_number_to_card(ss)
    elif drill_type == "Card → Number":
        _manual_card_to_number(ss)
    else:
        _manual_mixed(ss)

    st.markdown("---")
    _stack_view()


def _manual_number_to_card(ss):
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
        # safe: before text_input instantiation
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


def _manual_card_to_number(ss):
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


def _manual_mixed(ss):
    """
    Randomly choose Number→Card OR Card→Number for each question.
    User answers appropriately; stats combined.
    """
    col1, col2 = st.columns(2)
    with col1:
        mixed_start = st.number_input(
            "Start position (range for mixed)", 1, 52, 1, key="mn_manual_mixed_start"
        )
    with col2:
        mixed_end = st.number_input(
            "End position (range for mixed)", 1, 52, 52, key="mn_manual_mixed_end"
        )

    if mixed_start > mixed_end:
        st.error("Start position must be ≤ end position.")
        return

    if st.button("🎲 New mixed question", key="mn_manual_mixed_new"):
        # randomly pick mode
        mode = random.choice(["num_to_card", "card_to_num"])
        ss.mn_manual_mixed_mode = mode
        if mode == "num_to_card":
            pos = random.randint(mixed_start, mixed_end)
            ss.mn_manual_mixed_pos = pos
            ss.mn_manual_mixed_card = None
        else:
            idx = random.randint(mixed_start - 1, mixed_end - 1)
            ss.mn_manual_mixed_card = MNEMONICA[idx]
            ss.mn_manual_mixed_pos = None
        ss["mn_manual_mixed_answer_input"] = ""

    mode = ss.mn_manual_mixed_mode

    if mode is None:
        st.info("Click **New mixed question** to start.")
        return

    # NUMBER → CARD branch
    if mode == "num_to_card":
        pos = ss.mn_manual_mixed_pos
        if pos is None:
            return
        card = MNEMONICA[pos - 1]

        st.markdown(f"### Mixed drill – Position: `{pos}`")
        st.caption(f"(Range: {mixed_start}–{mixed_end}, expecting a **card**)")
        st.info("Think of the card at this position, then type it below.")

        with st.expander("Reveal card"):
            st.markdown(format_card(card), unsafe_allow_html=True)

        ans = st.text_input(
            "Your answer (e.g. AS, 4C, QH)",
            key="mn_manual_mixed_answer_input",
        )

        if st.button("Check mixed answer", key="mn_manual_mixed_check"):
            user = normalize_card_input(ans)
            correct = card
            ss.mn_manual_mixed_attempts += 1
            if user == correct:
                ss.mn_manual_mixed_correct += 1
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. Correct card is: {format_card(card)}")

    # CARD → NUMBER branch
    else:
        card = ss.mn_manual_mixed_card
        if card is None:
            return
        pos = MNEMONICA_CARD_TO_POS[card]

        st.markdown("### Mixed drill – Card:")
        st.markdown(format_card(card), unsafe_allow_html=True)
        st.caption(f"(Range: {mixed_start}–{mixed_end}, expecting a **position**)")
        st.info("Think of the position of this card in Mnemonica, then type it below.")

        with st.expander("Reveal position"):
            st.markdown(f"**Position:** `{pos}`")

        ans_num = st.text_input(
            "Your answer (position 1–52)",
            key="mn_manual_mixed_answer_input",
        )

        if st.button("Check mixed answer", key="mn_manual_mixed_check"):
            try:
                user_pos = int(ans_num.strip())
            except (ValueError, AttributeError):
                user_pos = None

            ss.mn_manual_mixed_attempts += 1
            if user_pos == pos:
                ss.mn_manual_mixed_correct += 1
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. Correct position is: `{pos}`")

    # Mixed stats
    attempts = ss.mn_manual_mixed_attempts
    correct = ss.mn_manual_mixed_correct
    st.markdown("---")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Mixed attempts", attempts)
    with col_s2:
        if attempts > 0:
            pct = (correct / attempts) * 100
            st.metric("Mixed accuracy", f"{correct}/{attempts}", f"{pct:.0f}%")
        else:
            st.metric("Mixed accuracy", "–", "+0%")


# ===================== AUTO DRILLS (THINK ONLY) =====================
def mn_render_auto():
    ss = st.session_state

    # Auto state
    ss.setdefault("mn_auto_num_running", False)
    ss.setdefault("mn_auto_card_running", False)
    ss.setdefault("mn_auto_mixed_running", False)

    ss.setdefault("mn_auto_num_interval", 5)
    ss.setdefault("mn_auto_card_interval", 5)
    ss.setdefault("mn_auto_mixed_interval", 5)

    ss.setdefault("mn_auto_num_rounds", 0)
    ss.setdefault("mn_auto_card_rounds", 0)
    ss.setdefault("mn_auto_mixed_rounds", 0)

    st.title("🧠 Mnemonica – Auto drills")

    drill_type = st.selectbox(
        "Drill type",
        ["Number → Card", "Card → Number", "Mixed"],
        key="mn_auto_drill_type",
    )

    st.markdown(
        "In auto mode you **never type**:\n\n"
        "- A question appears.\n"
        "- You get a countdown (your chosen interval) to **think of the answer**.\n"
        "- The app then shows the **correct answer**.\n"
        "- Short pause, then the **next question** starts automatically.\n"
    )
    st.divider()

    if drill_type == "Number → Card":
        _auto_number_to_card(ss)
    elif drill_type == "Card → Number":
        _auto_card_to_number(ss)
    else:
        _auto_mixed(ss)

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

    # One full cycle per run
    pos = random.randint(start, end)
    card = MNEMONICA[pos - 1]
    ss.mn_auto_num_rounds += 1

    st.markdown(f"### Position: `{pos}`  _(range {start}–{end})_")
    st.caption(f"Auto questions this session: `{ss.mn_auto_num_rounds}`")

    st.info("Look at the position and **think of the card** in Mnemonica.")

    countdown(ss.mn_auto_num_interval, label="Think for")

    st.success("✅ Time! The card at this position is:")
    st.markdown(format_card(card), unsafe_allow_html=True)

    countdown(3, label="Next position in")

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


# ---------- AUTO: MIXED (think only) ----------
def _auto_mixed(ss):
    col1, col2 = st.columns(2)
    with col1:
        mixed_start = st.number_input(
            "Start position (range for mixed)", 1, 52, 1, key="mn_auto_mixed_start"
        )
    with col2:
        mixed_end = st.number_input(
            "End position (range for mixed)", 1, 52, 52, key="mn_auto_mixed_end"
        )

    if mixed_start > mixed_end:
        st.error("Start position must be ≤ end position.")
        return

    ss.mn_auto_mixed_interval = st.number_input(
        "Thinking time (seconds)",
        min_value=1,
        max_value=60,
        value=ss.mn_auto_mixed_interval,
        key="mn_auto_mixed_interval_input",
    )

    colc1, colc2, colc3 = st.columns(3)
    with colc1:
        if st.button("▶ Start session", key="mn_auto_mixed_start_btn"):
            ss.mn_auto_mixed_running = True
            rerun()
    with colc2:
        if st.button("⏹ Stop session", key="mn_auto_mixed_stop_btn"):
            ss.mn_auto_mixed_running = False
            rerun()
    with colc3:
        if st.button("🔄 Reset counter", key="mn_auto_mixed_reset_btn"):
            ss.mn_auto_mixed_rounds = 0
            rerun()

    st.markdown(
        f"**Status:** {'🟢 Running' if ss.mn_auto_mixed_running else '🔴 Stopped'}  "
        f"• Thinking time: `{ss.mn_auto_mixed_interval}` seconds"
    )

    if not ss.mn_auto_mixed_running:
        return

    # Choose randomly between Number→Card and Card→Number
    mode = random.choice(["num_to_card", "card_to_num"])
    ss.mn_auto_mixed_rounds += 1

    if mode == "num_to_card":
        pos = random.randint(mixed_start, mixed_end)
        card = MNEMONICA[pos - 1]

        st.markdown(f"### Mixed auto – Position: `{pos}`")
        st.caption(
            f"(Range: {mixed_start}–{mixed_end}, expect a **card** in your head)"
        )
        st.info("Look at the position and **think of the card**.")

        countdown(ss.mn_auto_mixed_interval, label="Think for")

        st.success("✅ Time! The card at this position is:")
        st.markdown(format_card(card), unsafe_allow_html=True)

    else:
        idx = random.randint(mixed_start - 1, mixed_end - 1)
        card = MNEMONICA[idx]
        pos = MNEMONICA_CARD_TO_POS[card]

        st.markdown("### Mixed auto – Card:")
        st.markdown(format_card(card), unsafe_allow_html=True)
        st.caption(
            f"(Range: {mixed_start}–{mixed_end}, expect a **position** in your head)"
        )
        st.info("Look at the card and **think of its Mnemonica position**.")

        countdown(ss.mn_auto_mixed_interval, label="Think for")

        st.success("✅ Time! The position of this card is:")
        st.markdown(f"**Position:** `{pos}`")

    st.caption(f"Mixed auto questions this session: `{ss.mn_auto_mixed_rounds}`")

    countdown(3, label="Next mixed drill in")

    rerun()

def mn_render_flashcards():
    ss = st.session_state

    # Flashcards state
    ss.setdefault("mn_flash_main_mode", "Number → Card")
    ss.setdefault("mn_flash_current_mode", None)
    ss.setdefault("mn_flash_pos", None)
    ss.setdefault("mn_flash_card", None)
    ss.setdefault("mn_flash_counter", 0)

    st.title("🧠 Mnemonica – Flashcards")

    st.markdown(
        """
Flashcards mode helps you **visually memorize** the Mnemonica stack.

Each flashcard has two sides:
- Front → the **question** (position or card)  
- Back → the **answer**  

Click the card itself to flip it with an animation.
"""
    )
    st.divider()

    # ---------- Mode + Range ----------
    main_mode = st.radio(
        "Flashcard mode",
        ("Number → Card", "Card → Number", "Mixed"),
        horizontal=True,
        key="mn_flash_main_mode_select",
    )
    ss.mn_flash_main_mode = main_mode

    col1, col2 = st.columns(2)
    with col1:
        start = st.number_input("Start position", 1, 52, 1, key="mn_flash_start")
    with col2:
        end = st.number_input("End position", 1, 52, 52, key="mn_flash_end")

    if start > end:
        st.error("Start position must be ≤ end position.")
        return

    # ---------- Controls Row ----------
    colb1, colb2 = st.columns([1, 1])
    with colb1:
        reset_clicked = st.button("🔄 Reset counter", key="mn_flash_reset")

    if reset_clicked:
        ss.mn_flash_counter = 0
        ss.mn_flash_current_mode = None
        ss.mn_flash_pos = None
        ss.mn_flash_card = None

    st.markdown(f"**Cards reviewed this session:** `{ss.mn_flash_counter}`")
    st.markdown("---")

    # ---------- Flashcard Rendering ----------
    mode = ss.mn_flash_current_mode

    # If no card yet → generate first one automatically
    if mode is None:
        ss.mn_flash_counter += 1
        if ss.mn_flash_main_mode == "Mixed":
            mode = random.choice(["Number → Card", "Card → Number"])
        else:
            mode = ss.mn_flash_main_mode
        ss.mn_flash_current_mode = mode

        if mode == "Number → Card":
            pos = random.randint(start, end)
            ss.mn_flash_pos = pos
            ss.mn_flash_card = MNEMONICA[pos - 1]
        else:
            idx = random.randint(start - 1, end - 1)
            card = MNEMONICA[idx]
            ss.mn_flash_card = card
            ss.mn_flash_pos = MNEMONICA_CARD_TO_POS[card]

    # Prepare card content
    if ss.mn_flash_current_mode == "Number → Card":
        question_html = f"<strong>{ss.mn_flash_pos}</strong>"
        answer_html = format_card(ss.mn_flash_card)
        question_label = "Position"
        answer_label = "Card"
    else:
        question_html = format_card(ss.mn_flash_card)
        answer_html = f"<strong>{ss.mn_flash_pos}</strong>"
        question_label = "Card"
        answer_label = "Position"

    card_id = f"mn_flash_{ss.mn_flash_counter}"

    # Render centered flip card
    _render_flip_card(
        question_html=question_html,
        answer_html=answer_html,
        question_label=question_label,
        answer_label=answer_label,
        card_id=card_id,
    )

        # ---------- Bottom Centered "New Card" ----------
    st.markdown(
        """
        <style>
        div.stButton {
    display: flex;
    justify-content: center;
}

div.stButton > button.new-card-btn {
    width: 220px !important;
    height: 44px;
    background: linear-gradient(135deg, #fafafa, #f3f3f3);
    border: 1px solid #ddd;
    border-radius: 10px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.08);
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}
div.stButton > button.new-card-btn:hover {
    background: linear-gradient(135deg, #ffffff, #f9f9f9);
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    transform: translateY(-1px);
}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Real working Streamlit button (centered, same width as card)
    new_clicked = st.button("🎴 New card", key="mn_flash_new_bottom", help="Show next flashcard", type="secondary")
    st.markdown(
        "<style>div.stButton button.new-card-btn {margin-top:-0.5rem;}</style>",
        unsafe_allow_html=True,
    )

    # Handle button logic
    if new_clicked:
        ss.mn_flash_counter += 1
        mode = (
            random.choice(["Number → Card", "Card → Number"])
            if ss.mn_flash_main_mode == "Mixed"
            else ss.mn_flash_main_mode
        )
        ss.mn_flash_current_mode = mode

        if mode == "Number → Card":
            pos = random.randint(start, end)
            ss.mn_flash_pos = pos
            ss.mn_flash_card = MNEMONICA[pos - 1]
        else:
            idx = random.randint(start - 1, end - 1)
            card = MNEMONICA[idx]
            ss.mn_flash_card = card
            ss.mn_flash_pos = MNEMONICA_CARD_TO_POS[card]

        st.rerun()




# ===================== STACK VIEW =====================
def _stack_view():
    with st.expander("📜 Show full Mnemonica stack"):
        st.write("Top of deck = position 1")
        for i, card in enumerate(MNEMONICA, start=1):
            st.markdown(f"{i:2d}: {format_card(card)}", unsafe_allow_html=True)


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
