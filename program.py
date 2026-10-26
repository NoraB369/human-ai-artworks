import os
import random
import pandas as pd
import streamlit as st

from PIL import Image
from PIL import ImageDraw

# ==========================================
# CONFIG
# ==========================================

NUM_ROUNDS = 10

HUMAN_DIR = "dataset/human-made"
AI_DIR = "dataset/ai-generated"

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")

# ==========================================
# PLACEHOLDER DATASET GENERATION
# ==========================================

def create_placeholder_image(
    filepath,
    color,
    text
):
    image = Image.new(
        "RGB",
        (512, 512),
        color
    )

    draw = ImageDraw.Draw(image)

    draw.text(
        (50, 240),
        text,
        fill="black"
    )

    image.save(filepath)


def generate_placeholder_dataset():

    os.makedirs(HUMAN_DIR, exist_ok=True)
    os.makedirs(AI_DIR, exist_ok=True)

    human_files = os.listdir(HUMAN_DIR)
    ai_files = os.listdir(AI_DIR)

    if len(human_files) == 0:

        for i in range(5):

            create_placeholder_image(
                os.path.join(
                    HUMAN_DIR,
                    f"human_{i}.png"
                ),
                (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(100, 255)
                ),
                f"HUMAN {i}"
            )

    if len(ai_files) == 0:

        for i in range(5):

            create_placeholder_image(
                os.path.join(
                    AI_DIR,
                    f"ai_{i}.png"
                ),
                (
                    random.randint(0, 120),
                    random.randint(0, 120),
                    random.randint(0, 120)
                ),
                f"AI {i}"
            )


generate_placeholder_dataset()

# ==========================================
# LOAD DATA
# ==========================================

def load_dataset():

    images = []

    for filename in os.listdir(HUMAN_DIR):

        if filename.lower().endswith(
            SUPPORTED_EXTENSIONS
        ):

            images.append({
                "path": os.path.join(
                    HUMAN_DIR,
                    filename
                ),
                "true_type": "Human-Made"
            })

    for filename in os.listdir(AI_DIR):

        if filename.lower().endswith(
            SUPPORTED_EXTENSIONS
        ):

            images.append({
                "path": os.path.join(
                    AI_DIR,
                    filename
                ),
                "true_type": "AI-Generated"
            })

    return images


ALL_IMAGES = load_dataset()

# ==========================================
# SESSION STATE
# ==========================================

if "round" not in st.session_state:
    st.session_state.round = 1

if "results" not in st.session_state:
    st.session_state.results = []

# ==========================================
# NEW ROUND
# ==========================================

def generate_round():

    image_a, image_b = random.sample(
        ALL_IMAGES,
        2
    )

    return {

        "image_a": image_a,
        "image_b": image_b,

        "display_label_a":
            random.choice([
                "Human-Made",
                "AI-Generated"
            ]),

        "display_label_b":
            random.choice([
                "Human-Made",
                "AI-Generated"
            ])
    }


if "current_round" not in st.session_state:

    st.session_state.current_round = (
        generate_round()
    )

# ==========================================
# FINISHED
# ==========================================

if st.session_state.round > NUM_ROUNDS:

    st.title("Experiment Complete")

    df = pd.DataFrame(
        st.session_state.results
    )

    accuracy = (

        df["guess_A_correct"].sum()
        +
        df["guess_B_correct"].sum()

    ) / (len(df) * 2)

    st.success(
        f"Classification Accuracy: "
        f"{accuracy*100:.1f}%"
    )

    st.dataframe(df)

    csv = df.to_csv(index=False)

    st.download_button(
        "Download Results",
        csv,
        "results.csv",
        "text/csv"
    )

    st.stop()

# ==========================================
# CURRENT ROUND
# ==========================================

round_data = (
    st.session_state.current_round
)

st.title(
    "Human vs AI Image Preference Study"
)

st.subheader(
    f"Round {st.session_state.round}"
    f" / {NUM_ROUNDS}"
)

# ==========================================
# SHOW IMAGES
# ==========================================

col1, col2 = st.columns(2)

with col1:

    st.image(
        round_data["image_a"]["path"],
        use_container_width=True
    )

    st.markdown(
        f"""
        **Image A**

        {round_data['display_label_a']}
        """
    )

with col2:

    st.image(
        round_data["image_b"]["path"],
        use_container_width=True
    )

    st.markdown(
        f"""
        **Image B**

        {round_data['display_label_b']}
        """
    )

# ==========================================
# USER QUESTIONS
# ==========================================

preference = st.radio(
    "Which image do you prefer?",
    [
        "Image A",
        "Image B"
    ]
)

guess_a = st.radio(
    "What is Image A?",
    [
        "Human-Made",
        "AI-Generated"
    ]
)

guess_b = st.radio(
    "What is Image B?",
    [
        "Human-Made",
        "AI-Generated"
    ],
    key="guess_b"
)

# ==========================================
# SUBMIT
# ==========================================

if st.button("Submit Round"):

    image_a = (
        round_data["image_a"]
    )

    image_b = (
        round_data["image_b"]
    )

    st.session_state.results.append({

        "round":
            st.session_state.round,

        "image_A":
            os.path.basename(
                image_a["path"]
            ),

        "image_B":
            os.path.basename(
                image_b["path"]
            ),

        "true_A":
            image_a["true_type"],

        "true_B":
            image_b["true_type"],

        "shown_label_A":
            round_data[
                "display_label_a"
            ],

        "shown_label_B":
            round_data[
                "display_label_b"
            ],

        "user_guess_A":
            guess_a,

        "user_guess_B":
            guess_b,

        "guess_A_correct":
            guess_a ==
            image_a["true_type"],

        "guess_B_correct":
            guess_b ==
            image_b["true_type"],

        "preference":
            preference
    })

    st.session_state.round += 1

    st.session_state.current_round = (
        generate_round()
    )

    st.rerun()
