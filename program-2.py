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

# Material Design 3 Token Stylesheet with Compact Viewport & Custom Radio Chips
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

    /* Ultra-compact container layout to prevent scrolling on artwork view */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1100px !important;
    }

    /* Typography hierarchy */
    p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #1d1b20 !important;
        font-family: "Roboto", system-ui, -apple-system, sans-serif !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.35rem !important;
    }

    /* Container Box Styling for questionnaire items */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #d5cedb !important;
        border-radius: 10px !important;
        background: #ffffff !important;
        padding: 8px 12px !important;
        margin-bottom: 4px !important;
        box-shadow: none !important;
    }

    /* Custom styling for horizontal 5-button radio options */
    [data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
        width: 100% !important;
    }

    [data-testid="stRadio"] [role="radiogroup"] label {
        background: #f5f1f8 !important;
        border: 1px solid #ded6e7 !important;
        border-radius: 8px !important;
        padding: 6px 4px !important;
        flex: 1 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        cursor: pointer;
        transition: 0.1s ease;
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
        font-size: 0.78rem !important;
        font-weight: 650 !important;
        color: #381e72 !important;
        margin: 0 !important;
        text-align: center !important;
    }

    [data-testid="stRadio"] input {
        display: none !important;
    }

    /* Compact artwork display to ensure zero scrolling */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 0.2rem;
        margin-bottom: 0.4rem;
    }
    [data-testid="stImage"] img {
        max-height: min(34vh, 300px) !important;
        width: 100% !important;
        object-fit: contain;
        border-radius: 12px;
        box-shadow: 0 3px 12px rgba(29, 27, 32, 0.08);
    }

    /* M3 Typography & Metadata Tokens */
    .round-indicator {
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        color: #49454f !important;
        text-transform: uppercase;
        margin-bottom: 0.15rem;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1d1b20 !important;
        margin-bottom: 0.15rem;
    }
    .meta-tag {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        padding: 3px 10px;
        border-radius: 6px;
        background: #e8def8;
        color: #1d192b !important;
        margin-bottom: 0.3rem;
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

    /* Primary Button */
    div.stButton > button[kind="primary"] {
        background-color: #6750a4 !important;
        color: #ffffff !important;
        border-radius: 16px !important;
        height: 42px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        border: none !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15) !important;
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

    /* Secondary Choice Buttons */
    div.stButton > button[kind="secondary"] {
        background-color: #f3edf7 !important;
        color: #1d1b20 !important;
        border: 1px solid #cac4d0 !important;
        border-radius: 16px !important;
        height: 40px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
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
    }

    div.stButton > button[kind="primary"]:disabled {
        background-color: #1d1b201f !important;
        color: #1d1b2061 !important;
    }

    /* Short-answer text box */
    .stTextArea textarea {
        color: #1d1b20 !important;
        background-color: #ffffff !important;
        border: 1px solid #cac4d0 !important;
        border-radius: 8px !important;
        caret-color: #6750a4 !important;
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
                {"path": os.path.join(AI_DIR, filename), "true_type": "AI-Generated"}
            )
    return images

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
    st.error("Insufficient images: minimum 10 human-made and 10 AI-generated images required.")
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
# 1. INTRO PAGE
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
# 2. PRE-STUDY QUESTIONNAIRE
# ---------------------------------------------------------
if st.session_state.page == "pre_study":
    LIKERT_OPTIONS = [
        "Strongly agree",
        "Agree",
        "Neutral",
        "Disagree",
        "Strongly disagree",
    ]

    st.markdown(
        '<span class="meta-tag">Pre-Study Questionnaire</span>',
        unsafe_allow_html=True
    )

    st.subheader("Before We Begin")
    st.write(
        "Please answer the following questions "
        "before starting the artwork evaluation."
    )
    # ----------------------------------
    # Short Response Questions
    # ----------------------------------
    age = st.text_area(
        "How old are you?",
        height=50
    )
    gender = st.text_area(
        "What is your gender?",
        height=50
    )

    major = st.text_area(
        "What is your major?",
        height=50
    )
    
    ATTITUDE_STATEMENTS = [
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

    attitudes = {}
    for i, statement in enumerate(ATTITUDE_STATEMENTS):
        q_num = i + 1
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="font-size:10px; color:#6750a4; font-weight:700; margin-bottom:2px;">
                    QUESTION {q_num:02d}
                </div>
                <div style="font-size:13px; font-weight:500; color:#1d1b20; margin-bottom:6px;">
                    {statement}
                </div>
                """,
                unsafe_allow_html=True,
            )
            attitudes[f"attitude_{q_num}"] = st.radio(
                f"Attitude {q_num}",
                options=LIKERT_OPTIONS,
                index=None,
                horizontal=True,
                label_visibility="collapsed",
                key=f"attitude_radio_{q_num}"
            )

    # ----------------------------------
    # Likert Scale
    # ----------------------------------
    confidence = st.slider(
        "I am confident in my ability to detect when something is generated by AI. ",
        1,
        5,
        3,
        help="1 = Not confident, 5 = Extremely confident"
    )
    # ----------------------------------
    # Short Response Questions (Cont.)
    # ----------------------------------
    accuracy = st.text_area(
        "How accurate do you think you will be in selecting the AI-generated image? (0%-100% scale)",
        height=50
    )

    # ----------------------------------
    # Check if all questions are answered
    # ----------------------------------
    all_answered = (
        age.strip() != ""
        and gender.strip() != ""
        and major.strip() != ""
        and all(attitudes[f"attitude_{i}"] is not None for i in range(1, 22))
        and accuracy.strip() != ""
    )
    # ----------------------------------
    # Continue Button
    # ----------------------------------
    if st.button(
        "Continue to Study →",
        type="primary",
        use_container_width=True,
        disabled=not all_answered
    ):
        result_entry = {
            "age": age,
            "gender": gender,
            "major": major,
            **{k: v for k, v in attitudes.items()},
            "confidence": confidence,
            "accuracy": accuracy
        }
        st.session_state.pre_study = [result_entry]
        st.session_state.page = "experiment"
        st.rerun()
    st.stop()
    
# ---------------------------------------------------------
# 2. EXPERIMENT PAGE (RESPONSIVE SINGLE-VIEWPORT)
# ---------------------------------------------------------
if st.session_state.page == "experiment":
    if st.session_state.round > NUM_ROUNDS:
        st.session_state.page = "results"
        st.rerun()

    round_data = st.session_state.current_round

    st.markdown(
        f'<div class="round-indicator">Round {st.session_state.round} of {NUM_ROUNDS}</div>',
        unsafe_allow_html=True,
    )
    st.progress(st.session_state.round / NUM_ROUNDS)

    # State keys for current round
    guess_a_key = f"guess_a_{st.session_state.round}"
    guess_b_key = f"guess_b_{st.session_state.round}"
    pref_key = f"pref_{st.session_state.round}"

    # Side-by-side artwork evaluation
    col_a, col_b = st.columns(2, gap="medium")

    with col_a:
        st.markdown('<div class="card-title">Artwork A</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="meta-tag">Catalog: {round_data["display_label_a"]}</span>',
            unsafe_allow_html=True,
        )
        st.image(round_data["image_a"]["path"], use_container_width=True)
        
        st.markdown('<p style="font-size: 0.8rem; font-weight: 500; color: #49454f; margin-bottom: 0.2rem;">Artwork A is:</p>', unsafe_allow_html=True)
        current_guess_a = st.session_state.get(guess_a_key)
        
        ga_col1, ga_col2 = st.columns(2, gap="small")
        with ga_col1:
            if st.button("Human-Made", key=f"btn_ga_h_{st.session_state.round}", use_container_width=True, type="primary" if current_guess_a == "Human-Made" else "secondary"):
                st.session_state[guess_a_key] = "Human-Made"
                st.rerun()
        with ga_col2:
            if st.button("AI-Generated", key=f"btn_ga_ai_{st.session_state.round}", use_container_width=True, type="primary" if current_guess_a == "AI-Generated" else "secondary"):
                st.session_state[guess_a_key] = "AI-Generated"
                st.rerun()

    with col_b:
        st.markdown('<div class="card-title">Artwork B</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="meta-tag">Catalog: {round_data["display_label_b"]}</span>',
            unsafe_allow_html=True,
        )
        st.image(round_data["image_b"]["path"], use_container_width=True)
        
        st.markdown('<p style="font-size: 0.8rem; font-weight: 500; color: #49454f; margin-bottom: 0.2rem;">Artwork B is:</p>', unsafe_allow_html=True)
        current_guess_b = st.session_state.get(guess_b_key)
        
        gb_col1, gb_col2 = st.columns(2, gap="small")
        with gb_col1:
            if st.button("Human-Made", key=f"btn_gb_h_{st.session_state.round}", use_container_width=True, type="primary" if current_guess_b == "Human-Made" else "secondary"):
                st.session_state[guess_b_key] = "Human-Made"
                st.rerun()
        with gb_col2:
            if st.button("AI-Generated", key=f"btn_gb_ai_{st.session_state.round}", use_container_width=True, type="primary" if current_guess_b == "AI-Generated" else "secondary"):
                st.session_state[guess_b_key] = "AI-Generated"
                st.rerun()

    st.markdown('<hr style="margin: 0.4rem 0; border: none; border-top: 1px solid #e7e0ec;">', unsafe_allow_html=True)

    # Preference selection & submission bar
    pref_col, btn_col = st.columns([1.3, 1], gap="medium", vertical_alignment="center")

    with pref_col:
        st.markdown('<p style="font-size: 0.8rem; font-weight: 500; color: #49454f; margin-bottom: 0.2rem;">Preferred Artwork:</p>', unsafe_allow_html=True)
        current_pref = st.session_state.get(pref_key)
        
        p_col1, p_col2 = st.columns(2, gap="small")
        with p_col1:
            if st.button("Artwork A", key=f"btn_pref_a_{st.session_state.round}", use_container_width=True, type="primary" if current_pref == "Artwork A" else "secondary"):
                st.session_state[pref_key] = "Artwork A"
                st.rerun()
        with p_col2:
            if st.button("Artwork B", key=f"btn_pref_b_{st.session_state.round}", use_container_width=True, type="primary" if current_pref == "Artwork B" else "secondary"):
                st.session_state[pref_key] = "Artwork B"
                st.rerun()

    # Check if all questions on this page are completed
    current_guess_a = st.session_state.get(guess_a_key)
    current_guess_b = st.session_state.get(guess_b_key)
    current_pref = st.session_state.get(pref_key)
    all_answered = (current_guess_a is not None) and (current_guess_b is not None) and (current_pref is not None)

    with btn_col:
        submit_btn = st.button(
            "Next Round →" if st.session_state.round < NUM_ROUNDS else "Submit & Finish →",
            type="primary",
            use_container_width=True,
            disabled=not all_answered,
            key=f"submit_{st.session_state.round}"
        )

    if submit_btn and all_answered:
        image_a = round_data["image_a"]
        image_b = round_data["image_b"]

        st.session_state.results.append(
            {
                "round": st.session_state.round,
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

        if st.session_state.round == NUM_ROUNDS:
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

                requests.post(WEB_APP_URL, json=payload, timeout=5)
            except Exception:
                pass

        st.session_state.round += 1
        if st.session_state.round <= NUM_ROUNDS:
            st.session_state.current_round = generate_round()
        st.rerun()


# ---------------------------------------------------------
# 3. RESULTS PAGE
# ---------------------------------------------------------
if st.session_state.page == "results":
    st.markdown('<span class="meta-tag">Study Complete</span>', unsafe_allow_html=True)
    st.subheader("Thank you for participating!")
    st.write("Your classifications and preferences have been securely recorded.")
    st.write("")

    df = pd.DataFrame(st.session_state.results)
    total_correct = int(df["guess_A_correct"].sum() + df["guess_B_correct"].sum())
    total_predictions = len(df) * 2 - 2
    accuracy = (total_correct / total_predictions) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Accuracy", f"{accuracy:.1f}%")
    m2.metric("Correct Guesses", f"{total_correct}/{total_predictions}")
    m3.metric("Rounds Evaluated", NUM_ROUNDS)

    st.write("")
    with st.expander("Inspect Detailed Session Data", expanded=True):
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")