import streamlit as st
import pandas as pd
import random
import os
from PIL import Image
from io import BytesIO

# =====================================================
# CONFIG
# =====================================================

NUM_ROUNDS = 10

HUMAN_DIR = "dataset/human-made"
AI_DIR = "dataset/ai-generated"

SUPPORTED = (".jpg", ".jpeg", ".png")

# =====================================================
# LOAD DATASET
# =====================================================

def load_dataset():

    images = []

    for file in os.listdir(HUMAN_DIR):
        if file.lower().endswith(SUPPORTED):
            images.append(
                {
                    "path": os.path.join(HUMAN_DIR, file),
                    "true_type": "Human-Made"
                }
            )

    for file in os.listdir(AI_DIR):
        if file.lower().endswith(SUPPORTED):
            images.append(
                {
                    "path": os.path.join(AI_DIR, file),
                    "true_type": "AI-Generated"
                }
            )

    return images


all_images = load_dataset()

if len(all_images) < 2:
    st.error("Need at least 2 images.")
    st.stop()

# =====================================================
# SESSION STATE
# =====================================================

if "round" not in st.session_state:
    st.session_state.round = 1

if "results" not in st.session_state:
    st.session_state.results = []

if "current_pair" not in st.session_state:

    imgA, imgB = random.sample(all_images, 2)

    st.session_state.current_pair = {
        "A": imgA,
        "B": imgB,
        "label_A": random.choice(
            ["Human-Made", "AI-Generated"]
        ),
        "label_B": random.choice(
            ["Human-Made", "AI-Generated"]
        )
    }

# =====================================================
# FINISHED
# =====================================================

if st.session_state.round > NUM_ROUNDS:

    st.title("Experiment Complete")

    df = pd.DataFrame(st.session_state.results)

    correct = (
        df["Guess_A_Correct"].sum() +
        df["Guess_B_Correct"].sum()
    )

    total = len(df) * 2

    accuracy = 100 * correct / total

    st.success(
        f"Classification Accuracy: {accuracy:.1f}%"
    )

    st.dataframe(df)

    csv = df.to_csv(index=False)

    st.download_button(
        label="Download Results CSV",
        data=csv,
        file_name="experiment_results.csv",
        mime="text/csv"
    )

    st.stop()

# =====================================================
# CURRENT ROUND
# =====================================================

pair = st.session_state.current_pair

st.title("Human vs AI Image Study")

st.subheader(
    f"Round {st.session_state.round} of {NUM_ROUNDS}"
)

# =====================================================
# DISPLAY IMAGES
# =====================================================

col1, col2 = st.columns(2)

with col1:

    imageA = Image.open(pair["A"]["path"])

    st.image(
        imageA,
        use_container_width=True
    )

    st.markdown(
        f"### Image A\n"
        f"Displayed Label: "
        f"**{pair['label_A']}**"
    )

with col2:

    imageB = Image.open(pair["B"]["path"])

    st.image(
        imageB,
        use_container_width=True
    )

    st.markdown(
        f"### Image B\n"
        f"Displayed Label: "
        f"**{pair['label_B']}**"
    )

st.divider()

# =====================================================
# USER INPUT
# =====================================================

preference = st.radio(
    "Which image do you prefer?",
    ["Image A", "Image B"]
)

guess_a = st.radio(
    "What do you think Image A actually is?",
    ["Human-Made", "AI-Generated"],
    key="guessA"
)

guess_b = st.radio(
    "What do you think Image B actually is?",
    ["Human-Made", "AI-Generated"],
    key="guessB"
)

# =====================================================
# SUBMIT ROUND
# =====================================================

if st.button("Submit Round"):

    st.session_state.results.append({

        "Round":
            st.session_state.round,

        "Image_A_Path":
            pair["A"]["path"],

        "Image_A_Truth":
            pair["A"]["true_type"],

        "Image_A_Displayed_Label":
            pair["label_A"],

        "Image_A_User_Guess":
            guess_a,

        "Guess_A_Correct":
            guess_a ==
            pair["A"]["true_type"],

        "Label_A_Correct":
            pair["label_A"] ==
            pair["A"]["true_type"],

        "Image_B_Path":
            pair["B"]["path"],

        "Image_B_Truth":
            pair["B"]["true_type"],

        "Image_B_Displayed_Label":
            pair["label_B"],

        "Image_B_User_Guess":
            guess_b,

        "Guess_B_Correct":
            guess_b ==
            pair["B"]["true_type"],

        "Label_B_Correct":
            pair["label_B"] ==
            pair["B"]["true_type"],

        "Preference":
            preference
    })

    st.session_state.round += 1

    if st.session_state.round <= NUM_ROUNDS:

        imgA, imgB = random.sample(
            all_images,
            2
        )

        st.session_state.current_pair = {

            "A": imgA,
            "B": imgB,

            "label_A":
                random.choice(
                    [
                        "Human-Made",
                        "AI-Generated"
                    ]
                ),

            "label_B":
                random.choice(
                    [
                        "Human-Made",
                        "AI-Generated"
                    ]
                )
        }

    st.rerun()
