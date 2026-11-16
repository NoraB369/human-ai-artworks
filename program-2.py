import base64
from io import BytesIO
import json
import os
import random
import pandas as pd
from PIL import Image, ImageDraw
import requests
import streamlit as st

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzFhfKVVRCVhbeS2gou4wC2mbHTYVCkA4p8WC6RUtgCuZSdGVZOJiKNQzdr1lDAom0bZA/exec"

# ---------------------------------------------------------
# CONFIGURATION & MATERIAL DESIGN 3 SETUP
# ---------------------------------------------------------
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

# Material Design 3 Token Stylesheet with High Contrast Fixes
st.markdown(
    """
    <style>
    /* Reset Streamlit default header */
    header[data-testid="stHeader"] {
        height: 2rem !important;
        background: transparent !important;
    }
    
    /* M3 Surface Background */
    .stApp {
        background-color: #fef7ff !important;
        font-family: "Roboto", system-ui, -apple-system, sans-serif !important;
        color: #1d1b20 !important;
    }

    /* Container layout */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1080px !important;
    }

    /* Typography hierarchy */
    p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #1d1b20 !important;
        font-family: "Roboto", system-ui, -apple-system, sans-serif !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.55rem;
    }

    /* Question Cards (Bordered Containers) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #d5cedb !important;
        border-radius: 12px !important;
        background: #ffffff !important;
        padding: 12px 14px !important;
        margin-bottom: 6px !important;
        box-shadow: none !important;
    }

    /* Questionnaire Text Inputs */
    .stTextInput input {
        background: #ffffff !important;
        border: 1px solid #cac4d0 !important;
        border-radius: 10px !important;
        min-height: 42px !important;
        color: #1d1b20 !important;
    }
    .stTextInput input:focus {
        border-color: #6750a4 !important;
        box-shadow: 0 0 0 2px #6750a422 !important;
    }

    /* Consistent Numbered 1–5 Response Chips */
    [data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        justify-content: space-between !important;
    }

    [data-testid="stRadio"] [role="radiogroup"] label {
        background: #f5f1f8 !important;
        border: 1px solid #ded6e7 !important;
        border-radius: 8px !important;
        padding: 6px 8px !important;
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
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: #381e72 !important;
        margin: 0 !important;
        text-align: center !important;
    }

    [data-testid="stRadio"] input {
        accent-color: #6750a4 !important;
    }

    /* Artwork Display Frame with Bottom-Right Label */
    .artwork-frame {
        position: relative;
        width: 100%;
        height: min(40vh, 360px);
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 0.25rem;
        margin-bottom: 0.5rem;
        overflow: hidden;
        border-radius: 14px;
        background: #f7f2fa;
    }

    .artwork-frame img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(29, 27, 32, 0.08);
    }

    .artwork-tag {
        position: absolute;
        right: 12px;
        bottom: 12px;
        z-index: 2;
        display: inline-block;
        padding: 5px 12px;
        background: #e8def8;
        color: #1d192b !important;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.14);
    }

    /* M3 Typography & Metadata Tokens */
    .round-indicator {
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        color: #49454f !important;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: 600;
        letter-spacing: 0em;
        color: #1d1b20 !important;
        margin-bottom: 0.2rem;
    }
    .meta-tag {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        padding: 4px 12px;
        border-radius: 8px;
        background: #e8def8;
        color: #1d192b !important;
        margin-bottom: 0.5rem;
    }
    .section-heading {
        font-size: 1.1rem;
        font-weight: 650;
        color: #1d1b20 !important;
        margin: 0.4rem 0 0.1rem 0;
    }
    .section-description {
        font-size: 0.85rem;
        color: #49454f !important;
        margin-bottom: 0.6rem;
    }

    /* Material 3 Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #6750a4 !important;
        border-radius: 4px;
    }
    .stProgress > div > div > div {
        background-color: #e7e0ec !important;
        border-radius: 4px;
    }

    /* Primary Button (Next Round / Submit) - Solid Filled Purple */
    div.stButton > button[kind="primary"] {
        background-color: #6750a4 !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        height: 46px !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.01em !important;
        border: none !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #7965af !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    div.stButton > button[kind="primary"] p, 
    div.stButton > button[kind="primary"] span {
        color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }

    /* Secondary Choice Buttons (Unselected Choice Chips) */
    div.stButton > button[kind="secondary"] {
        background-color: #f3edf7 !important;
        color: #1d1b20 !important;
        border: 1px solid #cac4d0 !important;
        border-radius: 20px !important;
        height: 44px !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #e6e0eb !important;
        border-color: #49454f !important;
    }
    div.stButton > button[kind="secondary"] p, 
    div.stButton > button[kind="secondary"] span {
        color: #1d1b20 !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
    }

    /* Disabled state for Primary button */
    div.stButton > button[kind="primary"]:disabled {
        background-color: #1d1b201f !important;
        color: #1d1b2061 !important;
        box-shadow: none !important;
    }
    div.stButton > button[kind="primary"]:disabled p, 
    div.stButton > button[kind="primary"]:disabled span {
        color: #1d1b2061 !important;
    }

    /* Responsive adjustments for smaller laptop viewports */
    @media (min-width: 769px) and (max-height: 820px) {
        .artwork-frame {
            height: 31vh !important;
        }
        .block-container {
            padding-top: 0.75rem !important;
            padding-bottom: 0.75rem !important;
        }
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# DATASET HELPERS
# ---------------------------------------------------------
def load_dataset():
    images = []
    for filename in os.listdir(HUMAN_DIR):
        if filename.lower().endswith(SUPPORTED_EXTENSIONS):
            images.append(
                {
                    "path": os.path.join(HUMAN_DIR, filename),
                    "true_type": "Human-Made",
                }
            )
    for filename in os.listdir(AI_DIR):
        if filename.lower().endswith(SUPPORTED_EXTENSIONS):
            images.append(
                {
                    "path": os.path.join(AI_DIR, filename),
                    "true_type": "AI-Generated",
                }
            )
    return images


def render_artwork(path, displayed_label):
    """Render artwork with an AI/Human tag in its bottom-right corner."""
    short_label = "AI" if displayed_label == "AI-Generated" else "Human"

    with Image.open(path) as source:
        artwork = source.copy()
        artwork.thumbnail((1600, 1200))

        buffer = BytesIO()
        artwork.save(buffer, format="PNG")

    encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"""
        <div class="artwork-frame">
            <img src="data:image/png;base64,{encoded_image}" alt="Artwork" />
            <span class="artwork-tag">{short_label}</span>
        </div>
    """


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
human_images = [img for img in ALL_IMAGES if img["true_type"] == "Human-Made"]
ai_images = [img for img in ALL_IMAGES if img["true_type"] == "AI-Generated"]

if len(human_images) < NUM_ROUNDS or len(ai_images) < NUM_ROUNDS:
    st.error(
        f"Insufficient images: minimum {NUM_ROUNDS} human-made and {NUM_ROUNDS} AI-generated images required."
    )
    st.stop()


def opposite_label(label):
    return "AI-Generated" if label == "Human-Made" else "Human-Made"


def assign_labels(truth_a, truth_b, label_condition):
    if label_condition == "correct":
        return truth_a, truth_b
    elif label_condition == "wrong":
        return opposite_label(truth_a), opposite_label(truth_b)
    else:
        if random.choice([True, False]):
            return opposite_label(truth_a), truth_b
        return truth_a, opposite_label(truth_b)


def generate_round():
    pair_type, label_condition = st.session_state.conditions.pop()

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
        image_a["true_type"], image_b["true_type"], label_condition
    )
    return {
        "condition": pair_type,
        "label_condition": label_condition,
        "image_a": image_a,
        "image_b": image_b,
        "display_label_a": label_a,
        "display_label_b": label_b,
    }


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


# ---------------------------------------------------------
# STATE INITIALIZATION
# ---------------------------------------------------------
if "page" not in st.session_state:
    reset_session()


# ---------------------------------------------------------
# 1. INTRO PAGE (ORIGINAL SCREEN — UNCHANGED)
# ---------------------------------------------------------
if st.session_state.page == "intro":
    st.markdown('<span class="meta-tag">Research Study</span>', unsafe_allow_html=True)
    st.subheader("Human vs. AI Artwork Perception")
    st.write(
        "This study investigates visual art perception, preference, and attribution across "
        f"**{NUM_ROUNDS} image pairs**."
    )

    st.markdown(
        """
- **Examine**: Compare the two artworks and review their catalog labels.
- **Evaluate**: Classify whether each is truly Human-Made or AI-Generated.
- **Decide**: Select the artwork you personally prefer.
        """
    )

    st.write("")
    if st.button("Begin Pre-Study Questions →", type="primary", use_container_width=True):
        st.session_state.page = "pre_study"
        st.rerun()

    st.stop()


# ---------------------------------------------------------
# 2. PRE-STUDY QUESTIONNAIRE (REDESIGNED UI)
# ---------------------------------------------------------
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
        "Artificial Intelligence is used to spy on people.",
    ]

    st.markdown(
        '<span class="meta-tag">Pre-Study Questionnaire</span>',
        unsafe_allow_html=True,
    )
    st.subheader("Before We Begin")
    st.write(
        "Please answer the following questions before starting the artwork evaluation."
    )

    # ----------------------------------
    # Section 1: Demographics
    # ----------------------------------
    st.markdown(
        '<div class="section-heading">01 &nbsp; About You</div>'
        '<div class="section-description">A few basic background questions.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        age = st.text_input("How old are you?", placeholder="e.g. 24", key="age_input")
    with c2:
        gender = st.text_input("What is your gender?", placeholder="Your gender", key="gender_input")
    with c3:
        major = st.text_input("What is your major?", placeholder="e.g. Design", key="major_input")

    st.divider()

    # ----------------------------------
    # Section 2: AI Attitude Statements
    # ----------------------------------
    st.markdown(
        '<div class="section-heading">02 &nbsp; Your Views on AI</div>'
        '<div class="section-description">'
        "How much do you agree or disagree with each statement? Select one number per question "
        "(1 = Strongly agree · 2 = Agree · 3 = Neutral · 4 = Disagree · 5 = Strongly disagree)."
        "</div>",
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(2, gap="medium")

    for i, question in enumerate(ATTITUDE_QUESTIONS):
        question_number = i + 1
        target_col = left_col if i < 11 else right_col

        with target_col:
            with st.container(border=True):
                # Number and question inside the box above the options
                st.markdown(
                    f"""
                    <div style="
                        font-size:11px;
                        color:#6750a4;
                        font-weight:700;
                        letter-spacing:0.05em;
                        margin-bottom:4px;">
                        QUESTION {question_number:02d}
                    </div>
                    <div style="
                        font-size:13.5px;
                        font-weight:500;
                        line-height:1.45;
                        color:#1d1b20;
                        margin-bottom:10px;">
                        {question}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.radio(
                    f"Response to question {question_number}",
                    options=list(LIKERT_OPTIONS.keys()),
                    format_func=lambda x: str(x),
                    horizontal=True,
                    index=None,
                    label_visibility="collapsed",
                    key=f"attitude_choice_{question_number}",
                )

                # Scale anchor labels directly below options inside the box
                st.markdown(
                    """
                    <div style="
                        display:flex;
                        justify-content:space-between;
                        font-size:10px;
                        color:#49454f;
                        margin-top:4px;
                        padding:0 2px;">
                        <span>Strongly agree</span>
                        <span>Agree</span>
                        <span>Neutral</span>
                        <span>Disagree</span>
                        <span>Strongly disagree</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()

    # ----------------------------------
    # Section 3: Confidence & Accuracy
    # ----------------------------------
    st.markdown(
        '<div class="section-heading">03 &nbsp; AI Detection Confidence</div>'
        '<div class="section-description">Before viewing the artworks, tell us what you expect.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        confidence = st.slider(
            "I am confident in my ability to detect when something is generated by AI.",
            min_value=1,
            max_value=5,
            value=3,
            key="confidence_input",
        )
        st.caption("1 = Not confident at all  ·  5 = Extremely confident")

        accuracy = st.text_input(
            "How accurate do you think you will be in selecting the AI-generated image? (0%-100% scale)",
            placeholder="Enter a percentage from 0 to 100",
            key="accuracy_input",
        )

    # ----------------------------------
    # Validation & Continue
    # ----------------------------------
    accuracy_clean = accuracy.strip().replace("%", "")
    valid_accuracy = accuracy_clean.isdigit() and 0 <= int(accuracy_clean) <= 100

    all_answered = (
        age.strip() != ""
        and gender.strip() != ""
        and major.strip() != ""
        and all(
            st.session_state.get(f"attitude_choice_{i}") is not None
            for i in range(1, 22)
        )
        and valid_accuracy
    )

    if not valid_accuracy and accuracy.strip() != "":
        st.caption("Please enter a valid percentage between 0 and 100.")
    elif not all_answered:
        st.caption("Complete all questions above to unlock the next step.")

    if st.button(
        "Continue to Study →",
        type="primary",
        use_container_width=True,
        disabled=not all_answered,
    ):
        st.session_state.pre_study = [
            {
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
                "accuracy": accuracy,
            }
        ]

        st.session_state.page = "experiment"
        st.rerun()

    st.stop()


# ---------------------------------------------------------
# 3. EXPERIMENT PAGE (RESPONSIVE SINGLE-VIEWPORT)
# ---------------------------------------------------------
if st.session_state.page == "experiment":
    if st.session_state.round > NUM_ROUNDS:
        st.session_state.page = "results"
        st.rerun()

    round_data = st.session_state.current_round
    current_round = st.session_state.round

    st.markdown(
        f'<div class="round-indicator">Round {current_round} of {NUM_ROUNDS}</div>',
        unsafe_allow_html=True,
    )
    st.progress(current_round / NUM_ROUNDS)

    # State keys for current round
    guess_a_key = f"guess_a_{current_round}"
    guess_b_key = f"guess_b_{current_round}"
    pref_key = f"pref_{current_round}"

    # Side-by-side artwork evaluation
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown('<div class="card-title">Artwork A</div>', unsafe_allow_html=True)
        st.markdown(
            render_artwork(
                round_data["image_a"]["path"],
                round_data["display_label_a"],
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p style="font-size: 0.875rem; font-weight: 600; color: #49454f; margin-bottom: 0.35rem;">Artwork A is:</p>',
            unsafe_allow_html=True,
        )
        current_guess_a = st.session_state.get(guess_a_key)

        ga_col1, ga_col2 = st.columns(2, gap="small")
        with ga_col1:
            if st.button(
                "Human-Made",
                key=f"btn_ga_h_{current_round}",
                use_container_width=True,
                type="primary" if current_guess_a == "Human-Made" else "secondary",
            ):
                st.session_state[guess_a_key] = "Human-Made"
                st.rerun()
        with ga_col2:
            if st.button(
                "AI-Generated",
                key=f"btn_ga_ai_{current_round}",
                use_container_width=True,
                type="primary" if current_guess_a == "AI-Generated" else "secondary",
            ):
                st.session_state[guess_a_key] = "AI-Generated"
                st.rerun()

    with col_b:
        st.markdown('<div class="card-title">Artwork B</div>', unsafe_allow_html=True)
        st.markdown(
            render_artwork(
                round_data["image_b"]["path"],
                round_data["display_label_b"],
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p style="font-size: 0.875rem; font-weight: 600; color: #49454f; margin-bottom: 0.35rem;">Artwork B is:</p>',
            unsafe_allow_html=True,
        )
        current_guess_b = st.session_state.get(guess_b_key)

        gb_col1, gb_col2 = st.columns(2, gap="small")
        with gb_col1:
            if st.button(
                "Human-Made",
                key=f"btn_gb_h_{current_round}",
                use_container_width=True,
                type="primary" if current_guess_b == "Human-Made" else "secondary",
            ):
                st.session_state[guess_b_key] = "Human-Made"
                st.rerun()
        with gb_col2:
            if st.button(
                "AI-Generated",
                key=f"btn_gb_ai_{current_round}",
                use_container_width=True,
                type="primary" if current_guess_b == "AI-Generated" else "secondary",
            ):
                st.session_state[guess_b_key] = "AI-Generated"
                st.rerun()

    st.divider()

    # Preference selection & submission bar
    pref_col, btn_col = st.columns([1.3, 1], gap="medium", vertical_alignment="center")

    with pref_col:
        st.markdown(
            '<p style="font-size: 0.875rem; font-weight: 600; color: #49454f; margin-bottom: 0.35rem;">Preferred Artwork:</p>',
            unsafe_allow_html=True,
        )
        current_pref = st.session_state.get(pref_key)

        p_col1, p_col2 = st.columns(2, gap="small")
        with p_col1:
            if st.button(
                "Artwork A",
                key=f"btn_pref_a_{current_round}",
                use_container_width=True,
                type="primary" if current_pref == "Artwork A" else "secondary",
            ):
                st.session_state[pref_key] = "Artwork A"
                st.rerun()
        with p_col2:
            if st.button(
                "Artwork B",
                key=f"btn_pref_b_{current_round}",
                use_container_width=True,
                type="primary" if current_pref == "Artwork B" else "secondary",
            ):
                st.session_state[pref_key] = "Artwork B"
                st.rerun()

    # Check if all questions on this page are completed
    current_guess_a = st.session_state.get(guess_a_key)
    current_guess_b = st.session_state.get(guess_b_key)
    current_pref = st.session_state.get(pref_key)
    all_answered = (
        (current_guess_a is not None)
        and (current_guess_b is not None)
        and (current_pref is not None)
    )

    with btn_col:
        st.write("")
        submit_btn = st.button(
            "Next Round →" if current_round < NUM_ROUNDS else "Submit & Finish →",
            type="primary",
            use_container_width=True,
            disabled=not all_answered,
            key=f"submit_{current_round}",
        )

    if submit_btn and all_answered:
        image_a = round_data["image_a"]
        image_b = round_data["image_b"]

        st.session_state.results.append(
            {
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
                "guess_A_correct": current_guess_a == image_a["true_type"],
                "guess_B_correct": current_guess_b == image_b["true_type"],
                "preferred_image": current_pref,
            }
        )

        if current_round == NUM_ROUNDS:
            try:
                df_temp = pd.DataFrame(st.session_state.results)
                total_correct = int(
                    df_temp["guess_A_correct"].sum() + df_temp["guess_B_correct"].sum()
                )

                accuracy = float((total_correct / (NUM_ROUNDS * 2)) * 100)
                payload = {
                    "pre_study": st.session_state.pre_study,
                    "accuracy": accuracy,
                    "total_correct": total_correct,
                    "results": st.session_state.results,
                }

                requests.post(WEB_APP_URL, json=payload, timeout=10)
            except Exception:
                pass

        st.session_state.round += 1
        if st.session_state.round <= NUM_ROUNDS:
            st.session_state.current_round = generate_round()
        else:
            st.session_state.page = "results"
        st.rerun()


# ---------------------------------------------------------
# 4. RESULTS PAGE
# ---------------------------------------------------------
if st.session_state.page == "results":
    st.markdown('<span class="meta-tag">Study Complete</span>', unsafe_allow_html=True)
    st.subheader("Thank you for participating!")
    st.write("Your classifications and preferences have been securely recorded.")
    st.write("")

    df = pd.DataFrame(st.session_state.results)
    total_correct = int(df["guess_A_correct"].sum() + df["guess_B_correct"].sum())
    total_predictions = len(df) * 2
    accuracy = (total_correct / total_predictions) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Accuracy", f"{accuracy:.1f}%")
    m2.metric("Correct Guesses", f"{total_correct}/{total_predictions}")
    m3.metric("Rounds Evaluated", NUM_ROUNDS)

    st.write("")
    with st.expander("Inspect Detailed Session Data", expanded=True):
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")