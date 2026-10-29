import os
import random
import pandas as pd
import streamlit as st

from PIL import Image
from PIL import ImageDraw

# CONFIGURATION
NUM_ROUNDS = 10

HUMAN_DIR = "dataset/human-made"
AI_DIR = "dataset/ai-generated"

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Human vs AI Artwork Study",
    layout="centered"
)

# DATASET GENERATION
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

# LOAD DATASET
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

required_images = NUM_ROUNDS * 2

if len(ALL_IMAGES) < required_images:

    st.error(
        f"This study requires at least "
        f"{required_images} unique images.\n\n"
        f"Found only {len(ALL_IMAGES)} images."
    )

    st.stop()

# ROUND GENERATION
def generate_round():

    image_a = (
        st.session_state.image_pool.pop()
    )

    image_b = (
        st.session_state.image_pool.pop()
    )

    return {

        "image_a": image_a,

        "image_b": image_b,

        "display_label_a":
            random.choice(
                [
                    "Human-Made",
                    "AI-Generated"
                ]
            ),

        "display_label_b":
            random.choice(
                [
                    "Human-Made",
                    "AI-Generated"
                ]
            )
    }

# SESSION STATE
if "page" not in st.session_state:
    st.session_state.page = "intro"

if "round" not in st.session_state:
    st.session_state.round = 1

if "results" not in st.session_state:
    st.session_state.results = []

if "image_pool" not in st.session_state:

    st.session_state.image_pool = ALL_IMAGES.copy()

    random.shuffle(
        st.session_state.image_pool
    )

if "current_round" not in st.session_state:

    st.session_state.current_round = (
        generate_round()
    )

# INTRODUCTION PAGE
if st.session_state.page == "intro":

    st.title("Human vs AI Artwork Preference Study")

    st.markdown("---")

    st.header("Study Instructions")

    st.write("""
    For each round, 2 artworks will be displayed and labeled either "Human-Made" or "AI-Generated;" these labels may be correct or incorrect.
    Select which artwork you prefer, then identify whether you think each artwork is human-made or AI-generated.

    Click the button below when you are ready to begin!
    """)

    if st.button(
        "Start Study",
        use_container_width=True
    ):

        st.session_state.page = "experiment"

        st.rerun()

    st.stop()

# START EXPERIMENT
if (
    st.session_state.page == "experiment"
    and st.session_state.round > NUM_ROUNDS
):
    st.session_state.page = "results"
    st.rerun()

# EXPERIMENT PAGE
if st.session_state.page == "experiment":

    round_data = st.session_state.current_round

    st.title(
        "Human vs AI Artwork Preference Study"
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
            ### Artwork A

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
            ### Artwork B

            Displayed Label:
            **{round_data['display_label_b']}**
            """
        )

    st.markdown("---")

    preference = st.radio(
        "Which artwork do you prefer?",
        [
            "Image A",
            "Image B"
        ]
    )

    guess_a = st.radio(
        "What is Artwork A?",
        [
            "Human-Made",
            "AI-Generated"
        ],
        key=f"guess_a_{st.session_state.round}"
    )

    guess_b = st.radio(
        "What is Artwork B?",
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

# RESULTS PAGE
if st.session_state.page == "results":

    st.title("Thank You For Participating!")

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

    if st.button(
        "Restart Study",
        use_container_width=True
    ):
    
        st.session_state.page = "intro"
    
        st.session_state.round = 1
    
        st.session_state.results = []
    
        st.session_state.image_pool = (
            ALL_IMAGES.copy()
        )
    
        random.shuffle(
            st.session_state.image_pool
        )
    
        st.session_state.current_round = (
            generate_round()
        )
    
        st.rerun()

        st.session_state.page = "intro"
        st.session_state.round = 1
        st.session_state.results = []
        st.session_state.current_round = (
            generate_round()
        )

        st.rerun()
