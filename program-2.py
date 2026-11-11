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
    layout="centered",
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
        padding-top: 3.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 960px !important;
    }

    /* Typography hierarchy */
    p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #1d1b20 !important;
        font-family: "Roboto", system-ui, -apple-system, sans-serif !important;
    }

    /* Remove default boxed borders */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    /* Large artwork display with M3 Elevation */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 0.75rem;
        margin-bottom: 1rem;
    }
    [data-testid="stImage"] img {
        max-height: min(55vh, 480px) !important;
        width: 100% !important;
        object-fit: contain;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(29, 27, 32, 0.08);
    }

    /* M3 Typography & Metadata Tokens */
    .round-indicator {
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        color: #49454f !important;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .card-title {
        font-size: 1.25rem;
        font-weight: 500;
        letter-spacing: 0em;
        color: #1d1b20 !important;
        margin-bottom: 0.25rem;
    }
    .meta-tag {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.02em;
        padding: 4px 12px;
        border-radius: 8px;
        background: #e8def8;
        color: #1d192b !important;
        margin-bottom: 0.5rem;
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
        height: 48px !important;
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

    /* Secondary Choice Buttons (Unselected/Selected Choice Chips) - Clear contrast */
    div.stButton > button[kind="secondary"] {
        background-color: #f3edf7 !important;
        color: #1d1b20 !important;
        border: 1px solid #cac4d0 !important;
        border-radius: 20px !important;
        height: 46px !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
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
        font-size: 0.95rem !important;
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

    /* Material Design 3 dropdown styling */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1d1b20 !important;
        border: 1px solid #cac4d0 !important;
    }
    
    div[role="listbox"] {
        background-color: #ffffff !important;
    }
    
    div[role="option"] {
        color: #1d1b20 !important;
        background-color: #ffffff !important;
    }
    
    div[role="option"]:hover {
        background-color: #f3edf7 !important;
    }

    /* Short-answer text box */
    .stTextArea textarea {
        color: #ffffff !important;
        background-color: #2b2b2b !important;
        caret-color: #ffffff !important;
    }
    
    /* Placeholder text */
    .stTextArea textarea::placeholder {
        color: #cccccc !important;
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

CONDITIONS = [
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

ALL_IMAGES = load_dataset()
human_images = [img for img in ALL_IMAGES if img["true_type"] == "Human-Made"]
ai_images = [img for img in ALL_IMAGES if img["true_type"] == "AI-Generated"]

if len(human_images) < NUM_ROUNDS or len(ai_images) < NUM_ROUNDS:
    st.error("Insufficient images: minimum 50 human-made and 50 AI-generated images required.")
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
    st.session_state.results = []
    st.session_state.pre_study = {}
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
    # ----------------------------------
    # Multiple Choice Questions
    # ----------------------------------
    attitude_1 = st.selectbox(
        "For routine transactions, I would rather interact with an artificially intelligent system than with a human.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_2 = st.selectbox(
        "Artificial Intelligence can provide new economic opportunities for this country.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_3 = st.selectbox(
        "Organizations use Artificial Intelligence unethically.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_4 = st.selectbox(
        "Artificially intelligent systems can help people feel happier.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_5 = st.selectbox(
        "I am impressed by what Artificial Intelligence can do.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_6 = st.selectbox(
        "I think artificially intelligent systems make many errors.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_7 = st.selectbox(
        "I am interested in using artificially intelligent systems in my daily life.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_8 = st.selectbox(
        "I find Artificial Intelligence sinister.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_9 = st.selectbox(
        "Artificial Intelligence might take control of people.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_10 = st.selectbox(
        "I think Artificial Intelligence is dangerous.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_11 = st.selectbox(
        "Artificial Intelligence can have positive impacts on people’s wellbeing.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_12 = st.selectbox(
        "Artificial Intelligence is exciting.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_13 = st.selectbox(
        "I would be grateful if you could select 'Disagree' option.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_14 = st.selectbox(
        "An artificially intelligent agent would be better than an employee in many routine jobs.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_15 = st.selectbox(
        "There are many beneficial applications of Artificial Intelligence.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_16 = st.selectbox(
        "I shiver with discomfort when I think about future uses of Artificial Intelligence.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_17 = st.selectbox(
        "Artificially intelligent systems can perform better than humans.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_18 = st.selectbox(
        "Much of society will benefit from a future full of Artificial Intelligence.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_19 = st.selectbox(
        "I would like to use Artificial Intelligence in my own job.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_20 = st.selectbox(
        "People like me will suffer if Artificial Intelligence is used more and more.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
    )

    attitude_21 = st.selectbox(
        "Artificial Intelligence is used to spy on people.",
        [
            "Strongly agree",
            "Agree",
            "Neutral",
            "Disagree",
            "Strongly disagree",
        ],
        index=None,
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
        and attitude_1 is not None
        and attitude_2 is not None
        and attitude_3 is not None
        and attitude_4 is not None
        and attitude_5 is not None
        and attitude_6 is not None
        and attitude_7 is not None
        and attitude_8 is not None
        and attitude_9 is not None
        and attitude_10 is not None
        and attitude_11 is not None
        and attitude_12 is not None
        and attitude_13 is not None
        and attitude_14 is not None
        and attitude_15 is not None
        and attitude_16 is not None
        and attitude_17 is not None
        and attitude_18 is not None
        and attitude_19 is not None
        and attitude_20 is not None
        and attitude_21 is not None
        and age.strip() != ""
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
        st.session_state.pre_study = {
            "age": age,
            "gender": gender,
            "major": major,
            "attitude_1": attitude_1,
            "attitude_2": attitude_2,
            "attitude_3": attitude_3,
            "attitude_4": attitude_4,
            "attitude_5": attitude_5,
            "attitude_6": attitude_6,
            "attitude_7": attitude_7,
            "attitude_8": attitude_8,
            "attitude_9": attitude_9,
            "attitude_10": attitude_10,
            "attitude_11": attitude_11,
            "attitude_12": attitude_12,
            "attitude_13": attitude_13,
            "attitude_14": attitude_14,
            "attitude_15": attitude_15,
            "attitude_16": attitude_16,
            "attitude_17": attitude_17,
            "attitude_18": attitude_18,
            "attitude_19": attitude_19,
            "attitude_20": attitude_20,
            "attitude_21": attitude_21,
            "confidence": confidence,
            "accuracy": accuracy
        }

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
    st.write("")

    # State keys for current round
    guess_a_key = f"guess_a_{st.session_state.round}"
    guess_b_key = f"guess_b_{st.session_state.round}"
    pref_key = f"pref_{st.session_state.round}"

    # Side-by-side artwork evaluation
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown('<div class="card-title">Artwork A</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="meta-tag">Catalog: {round_data["display_label_a"]}</span>',
            unsafe_allow_html=True,
        )
        st.image(round_data["image_a"]["path"], use_container_width=True)
        
        st.markdown('<p style="font-size: 0.875rem; font-weight: 500; color: #49454f; margin-bottom: 0.4rem;">Artwork A is:</p>', unsafe_allow_html=True)
        current_guess_a = st.session_state.get(guess_a_key)
        
        ga_col1, ga_col2 = st.columns(2)
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
        
        st.markdown('<p style="font-size: 0.875rem; font-weight: 500; color: #49454f; margin-bottom: 0.4rem;">Artwork B is:</p>', unsafe_allow_html=True)
        current_guess_b = st.session_state.get(guess_b_key)
        
        gb_col1, gb_col2 = st.columns(2)
        with gb_col1:
            if st.button("Human-Made", key=f"btn_gb_h_{st.session_state.round}", use_container_width=True, type="primary" if current_guess_b == "Human-Made" else "secondary"):
                st.session_state[guess_b_key] = "Human-Made"
                st.rerun()
        with gb_col2:
            if st.button("AI-Generated", key=f"btn_gb_ai_{st.session_state.round}", use_container_width=True, type="primary" if current_guess_b == "AI-Generated" else "secondary"):
                st.session_state[guess_b_key] = "AI-Generated"
                st.rerun()

    st.write("")
    st.write("---")

    # Preference selection & submission bar
    pref_col, btn_col = st.columns([1.3, 1], gap="medium", vertical_alignment="center")

    with pref_col:
        st.markdown('<p style="font-size: 0.875rem; font-weight: 500; color: #49454f; margin-bottom: 0.4rem;">Preferred Artwork:</p>', unsafe_allow_html=True)
        current_pref = st.session_state.get(pref_key)
        
        p_col1, p_col2 = st.columns(2)
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
        st.write("")
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
    total_predictions = len(df) * 2
    accuracy = (total_correct / total_predictions) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Accuracy", f"{accuracy:.1f}%")
    m2.metric("Correct Guesses", f"{total_correct}/{total_predictions}")
    m3.metric("Rounds Evaluated", NUM_ROUNDS)

    st.write("")
    with st.expander("Inspect Detailed Session Data", expanded=False):
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        csv = df.to_csv(index=False)
        st.download_button(
            "Download Data (CSV)",
            csv,
            "artwork_study_results.csv",
            "text/csv",
            use_container_width=True,
        )
    with c2:
        if st.button("Start New Session", use_container_width=True):
            reset_session()
            st.rerun()
