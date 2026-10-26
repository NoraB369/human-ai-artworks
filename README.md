Human vs AI Image Preference Study
A Streamlit-based experiment for evaluating how people perceive and prefer human-created versus AI-generated images.

The application presents participants with two randomly selected images per round and asks them:

Which image they prefer.
Whether they believe each image is human-made or AI-generated.
Each participant completes 10 rounds, and all responses are recorded for later analysis.

Features
Random selection of image pairs
Human-made and AI-generated images mixed together
Random labeling of images
Labels may be correct or incorrect
Preference selection between two images
Classification of each image as Human-Made or AI-Generated
Automatic accuracy calculation
Downloadable CSV results file
Streamlit web interface
Project Structure
HumanVsAIStudy/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── dataset/
    ├── human-made/
    │   ├── image1.jpg
    │   ├── image2.png
    │   └── ...
    │
    └── ai-generated/
        ├── image1.jpg
        ├── image2.png
        └── ...
Dataset Setup
This repository does not include the image dataset.

Datasets containing images can easily exceed GitHub's file size recommendations and repository limits.

Create the following folder structure inside the project directory:

dataset/
├── human-made/
└── ai-generated/
Human-Made Images
Place all photographs, artwork, or images created by humans inside:

dataset/human-made/
Example:

dataset/human-made/
├── photo1.jpg
├── painting1.png
├── artwork2.jpg
└── ...
AI-Generated Images
Place all AI-generated images inside:

dataset/ai-generated/
Example:

dataset/ai-generated/
├── ai_image1.jpg
├── ai_image2.png
├── ai_image3.jpg
└── ...
Supported formats:

JPG
JPEG
PNG
Installation
Clone Repository
git clone https://github.com/YOUR_USERNAME/HumanVsAIStudy.git

cd HumanVsAIStudy
Create Virtual Environment (Recommended)
Windows:

python -m venv venv

venv\Scripts\activate
Mac/Linux:

python3 -m venv venv

source venv/bin/activate
Install Dependencies
pip install -r requirements.txt
Requirements
Example requirements.txt:

streamlit
pandas
pillow
Running the Application
Start the Streamlit server:

streamlit run app.py
The application will open automatically in your browser.

If it does not open automatically, navigate to:

http://localhost:8501
Experimental Procedure
Each participant completes 10 rounds.

For each round:

Two images are randomly selected from the dataset.
Images may come from:
Two human-made images
Two AI-generated images
One of each
Each image receives a displayed label:
Human-Made
AI-Generated
Displayed labels are assigned randomly and may be:
Correct
Incorrect
The participant:
Chooses their preferred image
Labels Image A as Human-Made or AI-Generated
Labels Image B as Human-Made or AI-Generated
Responses are stored for analysis.
After all rounds are completed:

Classification accuracy is calculated.
Results are displayed.
Results can be downloaded as a CSV file.
Output Data
The downloaded CSV contains information similar to:

Column	Description
Round	Round number
Image_A_Path	Path to Image A
Image_A_Truth	Actual image type
Image_A_Displayed_Label	Randomly displayed label
Image_A_User_Guess	User classification
Guess_A_Correct	Classification correctness
Label_A_Correct	Whether displayed label was correct
Image_B_Path	Path to Image B
Image_B_Truth	Actual image type
Image_B_Displayed_Label	Randomly displayed label
Image_B_User_Guess	User classification
Guess_B_Correct	Classification correctness
Label_B_Correct	Whether displayed label was correct
Preference	Preferred image
Example Research Questions
This study can be used to investigate:

Can people distinguish AI-generated images from human-created images?
Does incorrect labeling influence image preference?
Are AI-generated images preferred over human-made images?
Does perceived image origin affect aesthetic judgment?
How accurate are participants at identifying AI-generated content?
GitHub Notes
The dataset directory is intentionally excluded from version control.

Example .gitignore:

dataset/

__pycache__/
*.pyc
*.zip
*.rar
*.7z

.streamlit/*ecrets.toml
This allows the rpository to remain lightweight whie participants or researchers prov*de their own datasets locally.

--*

Future Improvements
Potentia* extensions include:

Participan* ID collection
Confidence rating*
Response time measurement
Dem*graphic questionnaire
Counterbal*nced image presentation
Larger n*mbers of rounds
Statistical summ*ries and visualizations
Database*backed data collection
Multi-use* deployment through Streamlit Clou*
License
This project isprovided for educational and reseach purposes.

Researchers are respnsible for ensuring they have the ight to use and distribute any datsets utilized with this applicatio.

Author
Created as a hu*an-versus-AI image perception and *reference experiment using Python and Streamlit.
