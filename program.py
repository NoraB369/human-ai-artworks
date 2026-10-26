import os
import random
import pandas as pd
import streamlit as st

from PIL import Image
from PIL import ImageDraw

# =====================================================
# CONFIGURATION
# =====================================================

NUM_ROUNDS = 10

HUMAN_DIR = "dataset/human-made"
AI_DIR = "dataset/ai-generated"

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Human vs AI Image Study",
    layout="wide"
)

# =====================================================
# PLACEHOLDER DATASET GENERATION
# =====================================================

def create_placeholder_image(filepath, color, text):

    image = Image.new(
        "RGB",
        (512, 512),
        color
    )

    draw = ImageDraw.Draw(image)

    draw.text(
        (150, 250),
        text,
        fill="black"
    )

    image.save(filepath)


def generate_placeholder_dataset():

    os.makedirs(HUMAN_DIR, exist_ok=True)
    os.makedirs(AI_DIR, exist_ok=True)

    human_files = [
        f for f in os.listdir(HUMAN_DIR)
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]

    ai_files = [
        f for f in os.listdir(AI_DIR)
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]

    if len(human_files) == 0:

        for i in range(5):

            create_placeholder_image(
                os.path.join(
                    HUMAN_DIR,
                    f"human_{i}.png"
                ),
                (
                    random.randint(150, 255),
                    random.randint(150, 255),
                    random.randint(150, 255)
                ),
                f"HUMAN {i + 1}"
            )

    if len(ai_files) == 0:

        for i in range(5):

            create_placeholder_image(
                os.path.join(
                    AI_DIR,
                    f"ai_{i}.png"
                ),
                (
                    random.randint(0, 100),
                    random.randint(0, 100),
                    random.randint(0, 100)
                ),
                f"AI {i + 1}"
            )


generate_placeholder_dataset()

# =====================================================
# DATASET LOADING
# =====================================================

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

# =====================================================
# ROUND GENERATION
# =====================================================

def generate_round():

    image_a, image_b = random.sample(
        ALL_IMAGES,
        2
    )

    return {

        "image_a": image_a,

        "image_b": image_b,

        "display_label_a": random.choice(
            [
                "Human-Made",
                "AI-Generated"
            ]
        ),

        "display_label_b": random.choice(
            [
                "Human-Made",
                "AI-Generated"
            ]
        )
    }

# =====================================================
# SESSION STATE
# =====================================================

if "page" not in st.session_state:
    st.session_state.page = "intro"

if "round" not in st.session_state:
    st.session_state.round = 1

if "results" not in st.session_state:
    st.session_state.results = []

if "current_round" not in st.session_state:
    st.session_state.current_round = (
        generate_round()
    )

# =====================================================
# INTRO PAGE
# =====================================================

if st.session_state.page == "intro":

    st.title("Human vs AI Image Preference Study")

    st.markdown("---")

    st.header("Study Instructions")

    st.write("""
    For each round:

    - Two images will be displayed.
    - Each image will have a label indicating
      whether it is supposedly Human-Made or
      AI-Generated.
    - These labels may be correct or incorrect.
    - Review both images carefully.
    - Select which image you prefer.
    - Identify whether you believe each image
      is Human-Made or AI-Generated.

    The study consists of 10 rounds.

    After completion you will be shown your
    classification accuracy and may download
    the results.

    Click the button below when you are ready
    to begin.
    """)

    if st.button(
        "Start Study",
        use_container_width=True
    ):

        st.session_state.page = "experiment"

        st.rerun()

    st.stop()

# =====================================================
# START RESULTS PAGE WHEN FINISHED
# =====================================================

if (
    st.session_state.page == "experiment"
    and st.session_state.round > NUM_ROUNDS
):
    st.session_state.page = "results"
    st.rerun()

# =====================================================
# EXPERIMENT PAGE
# =====================================================

if st.session_state.page == "experiment":

    round_data = st.session_state.current_round

    st.title(
        "Human vs AI Image Preference Study"
    )

    st.subheader(
        f"Round {st.session_state.round} of {NUM_ROUNDS}"
    )

    st.progress(
        st.session_state.round / NUM_ROUNDS
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.image(
            round_data["image_a"]["path"],
            use_container_width=True
        )

        st.markdown(
            f"""
            ### Image A

            Displayed Label:
            **{round_data['display_label_a']}**
            """
        )

    with col2:

        st.image(
            round_data["image_b"]["path"],
            use_container_width=True
        )

        st.markdown(
            f"""
            ### Image B

            Displayed Label:
            **{round_data['display_label_b']}**
            """
        )

    st.markdown("---")

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
        ],
        key=f"guess_a_{st.session_state.round}"
    )

    guess_b = st.radio(
        "What is Image B?",
        [
            "Human-Made",
            "AI-Generated"
        ],
        key=f"guess_b_{st.session_state.round}"
    )

    if st.button(
        "Submit Round",
        use_container_width=True
    ):

        image_a = round_data["image_a"]
        image_b = round_data["image_b"]

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

            "true_type_A":
                image_a["true_type"],

            "true_type_B":
                image_b["true_type"],

            "displayed_label_A":
                round_data[
                    "display_label_a"
                ],

            "displayed_label_B":
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

            "preferred_image":
                preference

        })

        st.session_state.round += 1

        st.session_state.current_round = (
            generate_round()
        )

        st.rerun()

# =====================================================
# RESULTS PAGE
# =====================================================

if st.session_state.page == "results":

    st.title("Study Complete")

    st.markdown("---")

    df = pd.DataFrame(
        st.session_state.results
    )

    total_correct = (

        df["guess_A_correct"].sum()
        +
        df["guess_B_correct"].sum()

    )

    total_predictions = len(df) * 2

    accuracy = (
        total_correct /
        total_predictions
    ) * 100

    st.success(
        f"Classification Accuracy: "
        f"{accuracy:.1f}%"
    )

    st.subheader("Results")

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = df.to_csv(
        index=False
    )

    st.download_button(
        "Download Results CSV",
        csv,
        "results.csv",
        "text/csv"
    )

    st.markdown("---")

    st.header("Thank You")

    st.write("""
    Thank you for participating in this study.

    Your responses have been recorded.

    You may download the results above
    or restart the study below.
    """)

    if st.button(
        "Restart Study",
        use_container_width=True
    ):

        st.session_state.page = "intro"
        st.session_state.round = 1
        st.session_state.results = []
        st.session_state.current_round = (
            generate_round()
        )

        st.rerun()
