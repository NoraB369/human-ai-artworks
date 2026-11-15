import base64
import json
import os
import random
from io import BytesIO
import pandas as pd
from PIL import Image, ImageDraw
import requests
import streamlit as st

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzFhfKVVRCVhbeS2gou4wC2mbHTYVCkA4p8WC6RUtgCuZSdGVZOJiKNQzdr1lDAom0bZA/exec"
NUM_ROUNDS = 50
HUMAN_DIR = "dataset/human-made"
AI_DIR = "dataset/ai-generated"
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")

st.set_page_config(
    page_title="Artwork Perception Study",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# DESIGN SYSTEM / CSS
# =========================================================

st.markdown("""
<style>

/* -------------------------------------------------------
   GLOBAL STYLING
------------------------------------------------------- */

.stApp {
    background-color: #fef7ff !important;
    font-family: "Roboto", system-ui, sans-serif !important;
    color: #1d1b20 !important;
}

.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 0.8rem !important;
    max-width: 1100px !important;
}

header[data-testid="stHeader"] {
    height: 2rem !important;
    background: transparent !important;
}

p, span, label, div, h1, h2, h3, h4 {
    font-family: "Roboto", system-ui, sans-serif !important;
    color: #1d1b20;
}

/* Remove unnecessary default spacing */
div[data-testid="stVerticalBlock"] {
    gap: 0.5rem;
}

/* -------------------------------------------------------
   TYPOGRAPHY
------------------------------------------------------- */

.round-indicator {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: #625d68 !important;
    text-transform: uppercase;
}

.card-title {
    font-size: 1.15rem;
    font-weight: 650;
    color: #1d1b20 !important;
    margin-bottom: 0.1rem;
}

.meta-tag {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 650;
    letter-spacing: 0.06em;
    padding: 5px 11px;
    border-radius: 7px;
    background: #eaddff;
    color: #381e72 !important;
    margin-bottom: 0.35rem;
}

.section-heading {
    font-size: 1.1rem;
    font-weight: 650;
    color: #29252f;
    margin: 0.4rem 0 0.1rem 0;
}

.section-description {
    font-size: 0.83rem;
    color: #625d68 !important;
    margin-bottom: 0.6rem;
}

/* -------------------------------------------------------
   QUESTIONNAIRE INPUT FIELDS
------------------------------------------------------- */

.stTextInput input {
    background: #ffffff !important;
    border: 1px solid #d5cedb !important;
    border-radius: 10px !important;
    min-height: 42px !important;
    color: #29252f !important;
}

.stTextInput input:focus {
    border-color: #6750a4 !important;
    box-shadow: 0 0 0 2px #6750a422 !important;
}

/* Question cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #e5deea !important;
    border-radius: 12px !important;
    background: #ffffff !important;
    padding: 9px 11px !important;
    margin-bottom: 5px !important;
    box-shadow: none !important;
}

/* -------------------------------------------------------
   CONSISTENT NUMBERED 1–5 RESPONSE CHIPS
------------------------------------------------------- */

[data-testid="stRadio"] [role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 6px !important;
    justify-content: space-between !important;
}

[data-testid="stRadio"] [role="radiogroup"] label {
    background: #f5f1f8 !important;
    border: 1px solid #ded6e7 !important;
    border-radius: 8px !important;
    padding: 4px 7px !important;
    min-width: 0 !important;
    flex: 1 !important;
    justify-content: center !important;
    transition: 0.15s ease;
}

[data-testid="stRadio"] [role="radiogroup"] label:hover {
    background: #eaddff !important;
    border-color: #6750a4 !important;
}

[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
    background: #eaddff !important;
    border: 1.5px solid #6750a4 !important;
}

[data-testid="stRadio"] [role="radiogroup"] label p {
    font-size: 0.85rem !important;
    font-weight: 650 !important;
    margin: 0 !important;
    text-align: center !important;
}

[data-testid="stRadio"] input {
    accent-color: #6750a4 !important;
}

/* Slider */
.stSlider [data-baseweb="slider"] div {
    background-color: #6750a4;
}

/* -------------------------------------------------------
   PROGRESS BAR
------------------------------------------------------- */

.stProgress > div > div > div > div {
    background-color: #6750a4 !important;
    border-radius: 4px;
}

.stProgress > div > div > div {
    background-color: #e7e0ec !important;
    border-radius: 4px;
}

/* -------------------------------------------------------
   BUTTONS
------------------------------------------------------- */

div.stButton > button[kind="primary"] {
    background-color: #6750a4 !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    height: 44px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border: none !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #7965af !important;
}

div.stButton > button[kind="primary"] p,
div.stButton > button[kind="primary"] span {
    color: #ffffff !important;
}

div.stButton > button[kind="secondary"] {
    background-color: #f3edf7 !important;
    color: #1d1b20 !important;
    border: 1px solid #cac4d0 !important;
    border-radius: 11px !important;
    height: 42px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    box-shadow: none !important;
}

div.stButton > button[kind="secondary"]:hover {
    background-color: #e6e0eb !important;
    border-color: #6750a4 !important;
}

div.stButton > button[kind="secondary"] p,
div.stButton > button[kind="secondary"] span {
    color: #1d1b20 !important;
}

div.stButton > button[kind="primary"]:disabled {
    background-color: #d8d3dc !important;
    color: #77717e !important;
}

/* -------------------------------------------------------
   ARTWORK DISPLAY WITH BOTTOM-RIGHT LABEL
------------------------------------------------------- */

.artwork-frame {
    position: relative;
    width: 100%;
    height: min(36vh, 320px);
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 0.2rem;
    margin-bottom: 0.35rem;
    overflow: hidden;
    border-radius: 12px;
}

.artwork-frame img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: 12px;
    box-shadow: 0 3px 12px rgba(29, 27, 32, 0.08);
}

/* AI / Human tag */
.artwork-tag {
    position: absolute;
    right: 12px;
    bottom: 12px;
    z-index: 2;

    display: inline-block;
    padding: 5px 11px;

    background: #eaddff;
    color: #381e72 !important;

    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;

    border-radius: 7px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

/* Artwork classification question */
.artwork-prompt {
    font-size: 0.83rem;
    font-weight: 600;
    color: #49454f !important;
    margin-top: 0.2rem;
    margin-bottom: 0.3rem;
}

/* -------------------------------------------------------
   SELECT BOX
------------------------------------------------------- */

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #1d1b20 !important;
    border: 1px solid #cac4d0 !important;
}

/* -------------------------------------------------------
   RESPONSIVE ADJUSTMENTS
------------------------------------------------------- */

@media (max-width: 768px) {

    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 0.4rem !important;
    }

    .artwork-frame {
        height: 28vh !important;
    }

    [data-testid="stRadio"] [role="radiogroup"] {
        gap: 3px !important;
    }

    [data-testid="stRadio"] [role="radiogroup"] label {
        padding: 4px 3px !important;
    }

    [data-testid="stRadio"] [role="radiogroup"] label p {
        font-size: 0.75rem !important;
    }
}

/* Short laptop screens */
@media (min-width: 769px) and (max-height: 800px) {

    .artwork-frame {
        height: 29vh !important;
    }

    .block-container {
        padding-top: 0.35rem !important;
        padding-bottom: 0.35rem !important;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATASET HELPERS
# =========================================================

def load_dataset():

    images = []

    for filename in os.listdir(HUMAN_DIR):

        if filename.lower().endswith(SUPPORTED_EXTENSIONS):

            images.append({
                "path": os.path.join(HUMAN_DIR, filename),
                "true_type": "Human-Made"
            })

    for filename in os.listdir(AI_DIR):

        if filename.lower().endswith(SUPPORTED_EXTENSIONS):

            images.append({
                "path": os.path.join(AI_DIR, filename),
                "true_type": "AI-Generated"
            })

    return images


def render_artwork(path, displayed_label):
    """Render artwork with an AI/Human tag in its bottom-right corner."""

    short_label = (
        "AI" if displayed_label == "AI-Generated" else "Human"
    )

    with Image.open(path) as source:
        artwork = source.copy()
        artwork.thumbnail((1600, 1200))

        buffer = BytesIO()
        artwork.save(buffer, format="PNG")

    encoded_image = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return f"""
        <div class="artwork-frame">
            <img
                src="data:image/png;base64,{encoded_image}"
                alt="Artwork"
            />
            <span class="artwork-tag">{short_label}</span>
        </div>
    """


# Preserve original experimental conditions
BASE_CONDITIONS = [
    ("HXH", "correct"),
    ("HXH", "wrong"),
    ("HXH", "one_wrong"),
    ("AXA", "correct"),
    ("AXA", "wrong"),
    ("AXA", "one_wrong"),
    ("AXH", "correct"),
    ("AXH", "wrong"),
    ("AXH", "one_wrong"),
    ("AXH", "one_wrong"),
]

CONDITIONS = []

while len(CONDITIONS) < NUM_ROUNDS:
    CONDITIONS.extend(BASE_CONDITIONS)

CONDITIONS = CONDITIONS[:NUM_ROUNDS]


ALL_IMAGES = load_dataset()

human_images = [
    img for img in ALL_IMAGES
    if img["true_type"] == "Human-Made"
]

ai_images = [
    img for img in ALL_IMAGES
    if img["true_type"] == "AI-Generated"
]


# Each 10-round block uses 10 human and 10 AI images.
# Therefore 50 rounds require at least 50 of each type.

if len(human_images) < NUM_ROUNDS or len(ai_images) < NUM_ROUNDS:

    st.error(
        f"Insufficient images. This experiment requires at least "
        f"{NUM_ROUNDS} human-made and {NUM_ROUNDS} AI-generated images."
    )

    st.stop()


def opposite_label(label):

    return (
        "AI-Generated"
        if label == "Human-Made"
        else "Human-Made"
    )


def assign_labels(truth_a, truth_b, label_condition):

    if label_condition == "correct":

        return truth_a, truth_b

    elif label_condition == "wrong":

        return (
            opposite_label(truth_a),
            opposite_label(truth_b)
        )

    else:

        if random.choice([True, False]):

            return opposite_label(truth_a), truth_b

        return truth_a, opposite_label(truth_b)


def generate_round():

    pair_type, label_condition = (
        st.session_state.conditions.pop()
    )

    if pair_type == "HXH":

        image_a = st.session_state.human_pool.pop()
        image_b = st.session_state.human_pool.pop()

    elif pair_type == "AXA":

        image_a = st.session_state.ai_pool.pop()
        image_b = st.session_state.ai_pool.pop()

    else:

        image_a = st.session_state.ai_pool.pop()
        image_b = st.session_state.human_pool.pop()

        if random.choice([True, False]):

            image_a, image_b = image_b, image_a

    label_a, label_b = assign_labels(
        image_a["true_type"],
        image_b["true_type"],
        label_condition
    )

    return {
        "condition": pair_type,
        "label_condition": label_condition,
        "image_a": image_a,
        "image_b": image_b,
        "display_label_a": label_a,
        "display_label_b": label_b
    }


# =========================================================
# SESSION RESET
# =========================================================

def reset_session():

    st.session_state.page = "intro"

    st.session_state.round = 1

    st.session_state.pre_study = []

    st.session_state.results = []

    st.session_state.human_pool = human_images.copy()

    st.session_state.ai_pool = ai_images.copy()

    random.shuffle(st.session_state.human_pool)
    random.shuffle(st.session_state.ai_pool)

    st.session_state.conditions = CONDITIONS.copy()

    random.shuffle(st.session_state.conditions)

    st.session_state.current_round = generate_round()


# =========================================================
# SESSION INITIALIZATION
# =========================================================

if "page" not in st.session_state:

    reset_session()


# =========================================================
# 1. INTRO PAGE
# ORIGINAL SCREEN — UNCHANGED
# =========================================================

if st.session_state.page == "intro":

    st.markdown(
        '<span class="meta-tag">RESEARCH STUDY</span>',
        unsafe_allow_html=True
    )

    st.title("Human vs. AI Artwork Perception")

    st.write(
        "Welcome! This study explores how people perceive, "
        "evaluate, and distinguish between human-made and "
        "AI-generated artwork."
    )

    st.write("")

    with st.container(border=True):

        st.markdown("### What you'll do")

        c1, c2, c3 = st.columns(3)

        with c1:

            st.markdown("**01 · Compare**")

            st.caption(
                "Examine two artworks and review their catalog labels."
            )

        with c2:

            st.markdown("**02 · Identify**")

            st.caption(
                "Decide whether each artwork is human-made or AI-generated."
            )

        with c3:

            st.markdown("**03 · Choose**")

            st.caption(
                "Select the artwork you personally prefer."
            )

    st.write("")

    st.info(
        f"The study contains {NUM_ROUNDS} image comparisons. "
        "Please complete the questions and evaluate each pair carefully."
    )

    st.write("")

    if st.button(
        "Begin Pre-Study Questionnaire →",
        type="primary",
        use_container_width=True
    ):

        st.session_state.page = "pre_study"

        st.rerun()

    st.stop()


# =========================================================
# 2. PRE-STUDY QUESTIONNAIRE
# ONE PAGE / REDESIGNED UI
# =========================================================

if st.session_state.page == "pre_study":

    LIKERT_OPTIONS = {
        1: "Strongly agree",
        2: "Agree",
        3: "Neutral",
        4: "Disagree",
        5: "Strongly disagree",
    }

    ATTITUDE_QUESTIONS = [

        "For routine transactions, I would rather interact with an artificially intelligent system than with a human.",

        "Artificial Intelligence can provide new economic opportunities for this country.",

        "Organizations use Artificial Intelligence unethically.",

        "Artificially intelligent systems can help people feel happier.",

        "I am impressed by what Artificial Intelligence can do.",

        "I think artificially intelligent systems make many errors.",

        "I am interested in using artificially intelligent systems in my daily life.",

        "I find Artificial Intelligence sinister.",

        "Artificial Intelligence might take control of people.",

        "I think Artificial Intelligence is dangerous.",

        "Artificial Intelligence can have positive impacts on people’s wellbeing.",

        "Artificial Intelligence is exciting.",

        "I would be grateful if you could select 'Disagree' option.",

        "An artificially intelligent agent would be better than an employee in many routine jobs.",

        "There are many beneficial applications of Artificial Intelligence.",

        "I shiver with discomfort when I think about future uses of Artificial Intelligence.",

        "Artificially intelligent systems can perform better than humans.",

        "Much of society will benefit from a future full of Artificial Intelligence.",

        "I would like to use Artificial Intelligence in my own job.",

        "People like me will suffer if Artificial Intelligence is used more and more.",

        "Artificial Intelligence is used to spy on people."

    ]

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    st.markdown(
        '<span class="meta-tag">PRE-STUDY QUESTIONNAIRE</span>',
        unsafe_allow_html=True
    )

    st.subheader("Before We Begin")

    st.caption(
        "Tell us a little about yourself and your perspectives on AI. "
        "There are no right or wrong answers."
    )

    # -----------------------------------------------------
    # SECTION 1: ABOUT YOU
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-heading">01 &nbsp; About You</div>'
        '<div class="section-description">'
        'A few basic background questions.'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:

        age = st.text_input(
            "Age",
            placeholder="e.g. 24",
            key="age_input"
        )

    with c2:

        gender = st.text_input(
            "Gender",
            placeholder="Your gender",
            key="gender_input"
        )

    with c3:

        major = st.text_input(
            "Major / Field of Study",
            placeholder="e.g. Design",
            key="major_input"
        )

    st.divider()

    # -----------------------------------------------------
    # SECTION 2: AI ATTITUDES
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-heading">02 &nbsp; Your Views on AI</div>'
        '<div class="section-description">'
        'How much do you agree or disagree with each statement? '
        'Select one number per question.'
        '</div>',
        unsafe_allow_html=True
    )

    # Response scale legend

    with st.container(border=True):

        legend_cols = st.columns(5)

        for col, (number, label) in zip(
            legend_cols,
            LIKERT_OPTIONS.items()
        ):

            with col:

                st.markdown(
                    f"""
                    <div style="text-align:center;">
                        <div style="
                            background:#eaddff;
                            color:#381e72;
                            border-radius:8px;
                            padding:5px;
                            font-weight:700;
                            font-size:15px;
                            margin-bottom:4px;">
                            {number}
                        </div>
                        <div style="
                            font-size:10px;
                            line-height:1.25;
                            color:#625d68;">
                            {label}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Two-column question layout

    left_col, right_col = st.columns(2, gap="medium")

    for i, question in enumerate(ATTITUDE_QUESTIONS):

        question_number = i + 1

        target_col = left_col if i < 11 else right_col

        with target_col:

            with st.container(border=True):

                st.markdown(
                    f"""
                    <div style="
                        font-size:11px;
                        color:#6750a4;
                        font-weight:700;
                        letter-spacing:0.05em;
                        margin-bottom:5px;">
                        QUESTION {question_number:02d}
                    </div>

                    <div style="
                        font-size:13px;
                        font-weight:500;
                        line-height:1.45;
                        color:#29252f;
                        margin-bottom:8px;">
                        {question}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.radio(
                    f"Response to question {question_number}",
                    options=list(LIKERT_OPTIONS.keys()),
                    format_func=lambda x: str(x),
                    horizontal=True,
                    index=None,
                    label_visibility="collapsed",
                    key=f"attitude_choice_{question_number}"
                )

    st.divider()

    # -----------------------------------------------------
    # SECTION 3: AI DETECTION CONFIDENCE
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-heading">03 &nbsp; AI Detection Confidence</div>'
        '<div class="section-description">'
        'Before viewing the artworks, tell us what you expect.'
        '</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):

        confidence = st.slider(
            "How confident are you in your ability to detect AI-generated artwork?",
            min_value=1,
            max_value=5,
            value=3,
            key="confidence_input"
        )

        st.caption(
            "1 = Not confident at all  ·  5 = Extremely confident"
        )

        accuracy = st.text_input(
            "How accurate do you expect to be at identifying AI-generated artwork?",
            placeholder="Enter a percentage from 0 to 100",
            key="accuracy_input"
        )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    accuracy_clean = accuracy.strip().replace("%", "")

    valid_accuracy = (
        accuracy_clean.isdigit()
        and 0 <= int(accuracy_clean) <= 100
    )

    all_answered = (
        age.strip() != ""
        and gender.strip() != ""
        and major.strip() != ""
        and all(
            st.session_state.get(
                f"attitude_choice_{i}"
            ) is not None
            for i in range(1, 22)
        )
        and valid_accuracy
    )

    if not valid_accuracy and accuracy.strip() != "":

        st.caption(
            "Please enter a valid percentage between 0 and 100."
        )

    if not all_answered:

        st.caption(
            "Complete all questions to unlock the next step."
        )

    # -----------------------------------------------------
    # CONTINUE BUTTON
    # -----------------------------------------------------

    if st.button(
        "Continue to Artwork Evaluation →",
        type="primary",
        use_container_width=True,
        disabled=not all_answered
    ):

        pre_study_answers = {

            "age": age,
            "gender": gender,
            "major": major,

            **{
                f"attitude_{i}": LIKERT_OPTIONS[
                    st.session_state[f"attitude_choice_{i}"]
                ]
                for i in range(1, 22)
            },

            "confidence": confidence,
            "accuracy": accuracy

        }

        # Store pre-study separately from experimental results
        st.session_state.pre_study = [pre_study_answers]

        st.session_state.page = "experiment"

        st.rerun()

    st.stop()


# =========================================================
# 3. EXPERIMENT PAGE
# RESPONSIVE SINGLE-VIEWPORT LAYOUT
# =========================================================

if st.session_state.page == "experiment":

    if st.session_state.round > NUM_ROUNDS:

        st.session_state.page = "results"

        st.rerun()

    round_data = st.session_state.current_round

    current_round = st.session_state.round

    # -----------------------------------------------------
    # ROUND HEADER
    # -----------------------------------------------------

    st.markdown(
        f'<div class="round-indicator">'
        f'ROUND {current_round} OF {NUM_ROUNDS}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.progress(current_round / NUM_ROUNDS)

    # -----------------------------------------------------
    # SESSION STATE KEYS
    # -----------------------------------------------------

    guess_a_key = f"guess_a_{current_round}"

    guess_b_key = f"guess_b_{current_round}"

    pref_key = f"pref_{current_round}"

    # -----------------------------------------------------
    # SIDE-BY-SIDE ARTWORK DISPLAY
    # -----------------------------------------------------

    col_a, col_b = st.columns(2, gap="large")

    with col_a:

        st.markdown(
            '<div class="card-title">Artwork A</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            render_artwork(
                round_data["image_a"]["path"],
                round_data["display_label_a"]
            ),
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="artwork-prompt">Artwork A is:</div>',
            unsafe_allow_html=True
        )

        current_guess_a = st.session_state.get(guess_a_key)

        ga_col1, ga_col2 = st.columns(2, gap="small")

        with ga_col1:

            if st.button(
                "Human-Made",
                key=f"btn_ga_h_{current_round}",
                use_container_width=True,
                type=(
                    "primary"
                    if current_guess_a == "Human-Made"
                    else "secondary"
                )
            ):

                st.session_state[guess_a_key] = "Human-Made"

                st.rerun()

        with ga_col2:

            if st.button(
                "AI-Generated",
                key=f"btn_ga_ai_{current_round}",
                use_container_width=True,
                type=(
                    "primary"
                    if current_guess_a == "AI-Generated"
                    else "secondary"
                )
            ):

                st.session_state[guess_a_key] = "AI-Generated"

                st.rerun()

    with col_b:

        st.markdown(
            '<div class="card-title">Artwork B</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            render_artwork(
                round_data["image_b"]["path"],
                round_data["display_label_b"]
            ),
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="artwork-prompt">Artwork B is:</div>',
            unsafe_allow_html=True
        )

        current_guess_b = st.session_state.get(guess_b_key)

        gb_col1, gb_col2 = st.columns(2, gap="small")

        with gb_col1:

            if st.button(
                "Human-Made",
                key=f"btn_gb_h_{current_round}",
                use_container_width=True,
                type=(
                    "primary"
                    if current_guess_b == "Human-Made"
                    else "secondary"
                )
            ):

                st.session_state[guess_b_key] = "Human-Made"

                st.rerun()

        with gb_col2:

            if st.button(
                "AI-Generated",
                key=f"btn_gb_ai_{current_round}",
                use_container_width=True,
                type=(
                    "primary"
                    if current_guess_b == "AI-Generated"
                    else "secondary"
                )
            ):

                st.session_state[guess_b_key] = "AI-Generated"

                st.rerun()

    # -----------------------------------------------------
    # PREFERENCE AND NEXT ROUND
    # -----------------------------------------------------

    st.divider()

    pref_col, btn_col = st.columns(
        [1.3, 1],
        gap="medium",
        vertical_alignment="center"
    )

    with pref_col:

        st.markdown(
            '<div class="artwork-prompt">'
            'Which artwork do you personally prefer?'
            '</div>',
            unsafe_allow_html=True
        )

        current_pref = st.session_state.get(pref_key)

        p_col1, p_col2 = st.columns(2, gap="small")

        with p_col1:

            if st.button(
                "Artwork A",
                key=f"btn_pref_a_{current_round}",
                use_container_width=True,
                type=(
                    "primary"
                    if current_pref == "Artwork A"
                    else "secondary"
                )
            ):

                st.session_state[pref_key] = "Artwork A"

                st.rerun()

        with p_col2:

            if st.button(
                "Artwork B",
                key=f"btn_pref_b_{current_round}",
                use_container_width=True,
                type=(
                    "primary"
                    if current_pref == "Artwork B"
                    else "secondary"
                )
            ):

                st.session_state[pref_key] = "Artwork B"

                st.rerun()

    # -----------------------------------------------------
    # CHECK COMPLETION
    # -----------------------------------------------------

    current_guess_a = st.session_state.get(guess_a_key)

    current_guess_b = st.session_state.get(guess_b_key)

    current_pref = st.session_state.get(pref_key)

    all_answered = (
        current_guess_a is not None
        and current_guess_b is not None
        and current_pref is not None
    )

    with btn_col:

        st.write("")

        submit_btn = st.button(
            (
                "Next Round →"
                if current_round < NUM_ROUNDS
                else "Submit & Finish →"
            ),
            type="primary",
            use_container_width=True,
            disabled=not all_answered,
            key=f"submit_{current_round}"
        )

    # -----------------------------------------------------
    # SAVE ROUND
    # -----------------------------------------------------

    if submit_btn and all_answered:

        image_a = round_data["image_a"]

        image_b = round_data["image_b"]

        st.session_state.results.append({

            "round": current_round,

            "condition": round_data["condition"],

            "label_condition": round_data["label_condition"],

            "image_A": os.path.basename(image_a["path"]),

            "image_B": os.path.basename(image_b["path"]),

            "true_type_A": image_a["true_type"],

            "true_type_B": image_b["true_type"],

            "displayed_label_A": round_data["display_label_a"],

            "displayed_label_B": round_data["display_label_b"],

            "user_guess_A": current_guess_a,

            "user_guess_B": current_guess_b,

            "guess_A_correct": (
                current_guess_a == image_a["true_type"]
            ),

            "guess_B_correct": (
                current_guess_b == image_b["true_type"]
            ),

            "preferred_image": current_pref,

        })

        # -------------------------------------------------
        # FINAL ROUND: SEND DATA TO GOOGLE SHEETS
        # -------------------------------------------------

        if current_round == NUM_ROUNDS:

            try:

                df_temp = pd.DataFrame(
                    st.session_state.results
                )

                total_correct = int(
                    df_temp["guess_A_correct"].sum()
                    + df_temp["guess_B_correct"].sum()
                )

                accuracy_percentage = float(
                    (total_correct / (NUM_ROUNDS * 2)) * 100
                )

                payload = {

                    "pre_study": st.session_state.pre_study,

                    "accuracy": accuracy_percentage,

                    "total_correct": total_correct,

                    "results": st.session_state.results,

                }

                response = requests.post(
                    WEB_APP_URL,
                    json=payload,
                    timeout=10
                )

                response.raise_for_status()

            except Exception as e:

                st.error(
                    "There was a problem submitting your responses. "
                    "Please contact the researcher."
                )

                st.error(str(e))

                st.stop()

        # -------------------------------------------------
        # ADVANCE ROUND
        # -------------------------------------------------

        st.session_state.round += 1

        if st.session_state.round <= NUM_ROUNDS:

            st.session_state.current_round = generate_round()

        else:

            st.session_state.page = "results"

        st.rerun()


# =========================================================
# 4. RESULTS PAGE
# =========================================================

if st.session_state.page == "results":

    st.markdown(
        '<span class="meta-tag">STUDY COMPLETE</span>',
        unsafe_allow_html=True
    )

    st.title("Thank You for Participating!")

    st.write(
        "Your artwork classifications and preferences "
        "have been submitted successfully."
    )

    st.write("")

    df = pd.DataFrame(st.session_state.results)

    total_correct = int(
        df["guess_A_correct"].sum()
        + df["guess_B_correct"].sum()
    )

    total_predictions = len(df) * 2

    accuracy = (
        total_correct / total_predictions
    ) * 100

    # -----------------------------------------------------
    # SUMMARY METRICS
    # -----------------------------------------------------

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Classification Accuracy",
        f"{accuracy:.1f}%"
    )

    m2.metric(
        "Correct Predictions",
        f"{total_correct}/{total_predictions}"
    )

    m3.metric(
        "Rounds Completed",
        f"{len(df)}/{NUM_ROUNDS}"
    )

    st.divider()

    # -----------------------------------------------------
    # OPTIONAL SESSION DATA
    # -----------------------------------------------------

    with st.expander(
        "Inspect Detailed Session Data",
        expanded=False
    ):

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    st.write("")

    st.caption(
        "Thank you for contributing to this research study!"
    )
