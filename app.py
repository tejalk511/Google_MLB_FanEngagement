import streamlit as st
import json
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

# Path to the service account key
key_path = 'mlbfanpage-3e9a02c2e6ef.json'

# Credentials from the service account key
credentials = Credentials.from_service_account_file(
    key_path,
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Refresh the credentials if expired
if credentials.expired:
    credentials.refresh(Request())

# Set the project and region
PROJECT_ID = 'mlbfanpage'
REGION = 'us-central1'

# Initialize Vertex AI and GenerativeModel
aiplatform.init(project=PROJECT_ID, location=REGION)
model = GenerativeModel("gemini-1.0-pro")

# Function to generate quiz questions based on team name
def generate_quiz_questions(team_name):
    prompt = f"Generate 5 quiz questions about {team_name} in MLB. Each question should have 4 options. Include the correct answer at the end of each question as (correct answer) and store in JSON format - Question, option1, option2, option3, option4, followed by answer in ans .. etc for 5 questions"
    response = model.generate_content(prompt)
    
    # Check the response text
    try:
        quiz_data = json.loads(response.text)  # Assuming the model returns JSON-like text
        return quiz_data
    except json.JSONDecodeError:
        return f"Error parsing JSON: {response.text}"

# Streamlit UI
st.title("MLB Quiz Game")

# Team selection using dropdown
team_name = st.selectbox("Select MLB Team:", ["Los Angeles Dodgers", "New York Yankees", "Chicago Cubs", "Miami Marlins", "Boston Red Sox"])

# Generate quiz questions when the button is pressed
if st.button("Generate Quiz Questions"):
    # Generate quiz questions based on the selected team
    quiz_questions = generate_quiz_questions(team_name)
    
    # Check if the response is valid
    if isinstance(quiz_questions, str):
        st.error(quiz_questions)  # Display the error message if any
    else:
        # Store quiz state in session state
        if 'current_question' not in st.session_state:
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.session_state.score = 0
            st.session_state.quiz_data = quiz_questions  # Store the quiz data in session state
        
        # Display the current question and options
        question_data = st.session_state.quiz_data[st.session_state.current_question]
        question = question_data['Question']
        options = [question_data['option1'], question_data['option2'], question_data['option3'], question_data['option4']]
        correct_answer = question_data['ans']  # The correct answer
        
        answer = st.radio(f"{question}", options)
        
        # When "Submit Answer" is clicked
        if st.button("Submit Answer"):
            if answer == correct_answer:
                st.session_state.score += 1  # Update score if the answer is correct
            st.session_state.current_question += 1  # Go to the next question

            # If all questions are answered, show the result
            if st.session_state.current_question == len(st.session_state.quiz_data):
                st.write(f"Quiz Finished! Your score is {st.session_state.score}/{len(st.session_state.quiz_data)}")
                
                # Optionally reset for a new quiz
                if st.button("Start New Quiz"):
                    st.session_state.current_question = 0
                    st.session_state.score = 0
