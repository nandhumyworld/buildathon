import streamlit as st
import pandas as pd
import json
import csv
import os
from datetime import datetime, timedelta
import uuid
import time
import threading
from typing import Dict, List, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="Prompt Battle Playground",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# File paths
ADMIN_DATA_FILE = 'admin_data.json'
RESULTS_FILE = 'results.json'
USERS_CSV_FILE = 'users.csv'

class DataManager:
    """Handles all data operations for JSON files"""
    
    @staticmethod
    def load_admin_data():
        """Load admin data from JSON file"""
        if os.path.exists(ADMIN_DATA_FILE):
            with open(ADMIN_DATA_FILE, 'r') as f:
                return json.load(f)
        return {
            'admins': [{'email': 'admin@example.com', 'password': 'admin123'}],
            'users': [],
            'questions': []
        }
    
    @staticmethod
    def save_admin_data(data):
        """Save admin data to JSON file"""
        with open(ADMIN_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_results():
        """Load results from JSON file"""
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    @staticmethod
    def save_results(results):
        """Save results to JSON file"""
        with open(RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2)

class UserManager:
    """Handles user-related operations"""
    
    @staticmethod
    def create_sample_csv():
        """Create sample CSV file if it doesn't exist"""
        if not os.path.exists(USERS_CSV_FILE):
            sample_data = [
                ['user_id', 'fullname', 'emailid', 'phonenumber', 'IsTechnical'],
                ['1', 'John Doe', 'john@example.com', '1234567890', 'yes'],
                ['2', 'Jane Smith', 'jane@example.com', '0987654321', 'no'],
                ['3', 'Alice Johnson', 'alice@example.com', '1122334455', 'yes'],
                ['4', 'Bob Wilson', 'bob@example.com', '9988776655', 'no'],
                ['5', 'Charlie Brown', 'charlie@example.com', '5566778899', 'yes']
            ]
            
            with open(USERS_CSV_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(sample_data)
    
    @staticmethod
    def import_users_from_csv():
        """Import users from CSV file"""
        admin_data = DataManager.load_admin_data()
        users = []
        
        if os.path.exists(USERS_CSV_FILE):
            df = pd.read_csv(USERS_CSV_FILE)
            for _, row in df.iterrows():
                user = {
                    'user_id': str(row['user_id']),
                    'fullname': row['fullname'],
                    'emailid': row['emailid'],
                    'phonenumber': str(row['phonenumber']),
                    'is_technical': str(row['IsTechnical']).lower() == 'yes',
                    'password': str(row['phonenumber'])  # Default password is phone number
                }
                users.append(user)
        
        admin_data['users'] = users
        DataManager.save_admin_data(admin_data)
        return users
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user login"""
        admin_data = DataManager.load_admin_data()
        
        for user in admin_data['users']:
            if user['emailid'] == email and user['password'] == password:
                return user
        return None
    
    @staticmethod
    def authenticate_admin(email, password):
        """Authenticate admin login"""
        admin_data = DataManager.load_admin_data()
        
        for admin in admin_data['admins']:
            if admin['email'] == email and admin['password'] == password:
                return admin
        return None
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        admin_data = DataManager.load_admin_data()
        return admin_data['users']

class QuestionManager:
    """Handles question-related operations"""
    
    @staticmethod
    def add_question(question_text):
        """Add a new question"""
        admin_data = DataManager.load_admin_data()
        
        question = {
            'id': str(uuid.uuid4()),
            'text': question_text,
            'created_at': datetime.now().isoformat()
        }
        
        admin_data['questions'].append(question)
        DataManager.save_admin_data(admin_data)
        return question
    
    @staticmethod
    def get_all_questions():
        """Get all questions"""
        admin_data = DataManager.load_admin_data()
        return admin_data['questions']
    
    @staticmethod
    def get_question_by_id(question_id):
        """Get question by ID"""
        admin_data = DataManager.load_admin_data()
        
        for question in admin_data['questions']:
            if question['id'] == question_id:
                return question
        return None

class GameManager:
    """Handles game session management"""
    
    def __init__(self):
        if 'game_sessions' not in st.session_state:
            st.session_state.game_sessions = {}
        if 'current_session_id' not in st.session_state:
            st.session_state.current_session_id = None
        if 'player_prompts' not in st.session_state:
            st.session_state.player_prompts = {}
    
    def create_session(self, question, timer_duration, selected_players):
        """Create a new game session"""
        session_id = str(uuid.uuid4())
        
        st.session_state.game_sessions[session_id] = {
            'question': question,
            'timer_duration': timer_duration,
            'selected_players': selected_players,
            'is_active': False,
            'start_time': None,
            'end_time': None,
            'player_prompts': {}
        }
        
        st.session_state.current_session_id = session_id
        return session_id
    
    def start_session(self, session_id):
        """Start a game session"""
        if session_id in st.session_state.game_sessions:
            st.session_state.game_sessions[session_id]['is_active'] = True
            st.session_state.game_sessions[session_id]['start_time'] = datetime.now()
            st.session_state.game_sessions[session_id]['end_time'] = (
                datetime.now() + timedelta(seconds=st.session_state.game_sessions[session_id]['timer_duration'])
            )
    
    def stop_session(self, session_id):
        """Stop a game session"""
        if session_id in st.session_state.game_sessions:
            st.session_state.game_sessions[session_id]['is_active'] = False
    
    def update_player_prompt(self, session_id, player_id, prompt):
        """Update player's prompt"""
        if session_id in st.session_state.game_sessions:
            st.session_state.game_sessions[session_id]['player_prompts'][player_id] = prompt

class LLMEvaluator:
    """Handles LLM evaluation (mock implementation)"""
    
    @staticmethod
    def evaluate_prompts(question, prompts):
        """Evaluate prompts using mock LLM"""
        try:
            evaluation_results = []
            
            for player, prompt in prompts.items():
                # Mock evaluation criteria
                relevance_score = min(10, len(prompt.split()) * 0.5)  # Simple word count scoring
                creativity_score = min(10, len(set(prompt.lower().split())) * 0.3)  # Unique words
                clarity_score = min(10, 10 - prompt.count(',') * 0.5) if ',' in prompt else 8
                
                total_score = (relevance_score + creativity_score + clarity_score) / 3
                
                evaluation_results.append({
                    'player': player,
                    'prompt': prompt,
                    'relevance': round(relevance_score, 1),
                    'creativity': round(creativity_score, 1),
                    'clarity': round(clarity_score, 1),
                    'total_score': round(total_score, 1)
                })
            
            # Sort by total score
            evaluation_results.sort(key=lambda x: x['total_score'], reverse=True)
            
            return evaluation_results
            
        except Exception as e:
            return f"Error in evaluation: {str(e)}"

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'

def login_page():
    """Login page interface"""
    st.title("🎮 Prompt Battle Playground")
    st.markdown("---")
    
    # Create sample CSV if it doesn't exist
    UserManager.create_sample_csv()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Choose Login Type")
        
        login_type = st.radio("", ["Admin Login", "Player Login"])
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if login_type == "Player Login":
                st.info("💡 Default password is your phone number (10 digits)")
            
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if login_type == "Admin Login":
                    admin = UserManager.authenticate_admin(email, password)
                    if admin:
                        st.session_state.logged_in = True
                        st.session_state.user_type = 'admin'
                        st.session_state.user_data = admin
                        st.session_state.current_page = 'dashboard'
                        st.success("Admin login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid admin credentials")
                
                else:  # Player Login
                    user = UserManager.authenticate_user(email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_type = 'player'
                        st.session_state.user_data = user
                        st.session_state.current_page = 'playground'
                        st.success(f"Welcome, {user['fullname']}!")
                        st.rerun()
                    else:
                        st.error("Invalid player credentials")
        
        # Sample credentials info
        with st.expander("📋 Sample Credentials"):
            st.markdown("""
            **Admin:**
            - Email: admin@example.com
            - Password: admin123
            
            **Sample Players:**
            - john@example.com / 1234567890
            - jane@example.com / 0987654321
            - alice@example.com / 1122334455
            """)

def admin_dashboard():
    """Admin dashboard interface"""
    st.title("🔧 Admin Dashboard")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### Welcome, Admin!")
        page = st.selectbox("Navigate to:", ["User Management", "Question Management", "Playground", "Results"])
    
    if page == "User Management":
        user_management_page()
    elif page == "Question Management":
        question_management_page()
    elif page == "Playground":
        st.session_state.current_page = 'playground'
        st.rerun()
    elif page == "Results":
        results_page()

def user_management_page():
    """User management interface"""
    st.header("👥 User Management")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("📥 Import Users from CSV", type="primary"):
            try:
                users = UserManager.import_users_from_csv()
                st.success(f"Successfully imported {len(users)} users!")
                st.rerun()
            except Exception as e:
                st.error(f"Error importing users: {str(e)}")
        
        if st.button("📄 View CSV Template"):
            st.info("""
            CSV Format:
            user_id,fullname,emailid,phonenumber,IsTechnical
            1,John Doe,john@example.com,1234567890,yes
            """)
    
    with col2:
        st.subheader("Current Users")
        users = UserManager.get_all_users()
        
        if users:
            df = pd.DataFrame(users)
            df['is_technical'] = df['is_technical'].map({True: 'Yes', False: 'No'})
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found. Please import users from CSV.")

def question_management_page():
    """Question management interface"""
    st.header("❓ Question Management")
    
    # Add new question
    with st.form("add_question_form"):
        st.subheader("Add New Question")
        new_question = st.text_area("Question Text", height=100)
        
        if st.form_submit_button("Add Question"):
            if new_question.strip():
                question = QuestionManager.add_question(new_question)
                st.success("Question added successfully!")
                st.rerun()
            else:
                st.error("Please enter a question")
    
    # Display existing questions
    st.subheader("Existing Questions")
    questions = QuestionManager.get_all_questions()
    
    if questions:
        for i, question in enumerate(questions):
            with st.expander(f"Question {i+1}: {question['text'][:50]}..."):
                st.write(f"**Full Question:** {question['text']}")
                st.write(f"**Created:** {question['created_at']}")
                st.write(f"**ID:** {question['id']}")
    else:
        st.info("No questions found. Add some questions to get started!")

def results_page():
    """Results viewing interface"""
    st.header("📊 Game Results")
    
    results = DataManager.load_results()
    
    if results:
        for i, result in enumerate(reversed(results)):  # Show latest first
            with st.expander(f"Game {len(results)-i} - {result['timestamp'][:19]}"):
                st.write(f"**Question:** {result['question']}")
                st.write(f"**Evaluation:**")
                
                if isinstance(result['evaluation'], list):
                    # Display as table
                    eval_df = pd.DataFrame(result['evaluation'])
                    st.dataframe(eval_df, use_container_width=True)
                else:
                    st.write(result['evaluation'])
                
                st.write("**Player Prompts:**")
                for player, prompt in result['prompts'].items():
                    st.write(f"- **{player}:** {prompt}")
    else:
        st.info("No game results found yet.")

def playground_page():
    """Main playground interface"""
    st.title("⚔️ Prompt Battle Playground")
    
    # Initialize game manager
    game_manager = GameManager()
    
    # Display timer
    timer_col1, timer_col2, timer_col3 = st.columns([1, 2, 1])
    with timer_col2:
        timer_placeholder = st.empty()
    
    # Admin controls
    if st.session_state.user_type == 'admin':
        with st.expander("🎛️ Admin Controls", expanded=True):
            admin_controls(game_manager, timer_placeholder)
    
    # Game area
    st.markdown("---")
    
    # Current question display
    current_session_id = st.session_state.current_session_id
    if current_session_id and current_session_id in st.session_state.game_sessions:
        session_data = st.session_state.game_sessions[current_session_id]
        
        st.subheader("📝 Current Question")
        st.info(session_data['question']['text'])
        
        # Player prompt areas
        st.subheader("✍️ Player Responses")
        
        if st.session_state.user_type == 'admin':
            # Admin can see all player prompts
            display_all_player_prompts(current_session_id, session_data)
        else:
            # Player can only see their own prompt area
            display_player_prompt_area(current_session_id)
        
        # Timer logic
        if session_data['is_active']:
            display_timer(timer_placeholder, session_data)
    else:
        st.info("No active game session. Admin can start a new game using the controls above.")

def admin_controls(game_manager, timer_placeholder):
    """Admin control panel"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("⏰ Timer")
        minutes = st.number_input("Minutes", min_value=0, max_value=60, value=5)
        seconds = st.number_input("Seconds", min_value=0, max_value=59, value=0)
        timer_duration = minutes * 60 + seconds
    
    with col2:
        st.subheader("👥 Players")
        users = UserManager.get_all_users()
        if users:
            user_options = {f"{user['fullname']} ({user['emailid']})": user for user in users}
            selected_users = st.multiselect(
                "Select Players",
                options=list(user_options.keys()),
                default=list(user_options.keys())[:2]
            )
            selected_player_data = [user_options[user] for user in selected_users]
        else:
            st.warning("No users available. Please import users first.")
            selected_player_data = []
    
    with col3:
        st.subheader("❓ Questions")
        questions = QuestionManager.get_all_questions()
        if questions:
            question_options = {f"Q{i+1}: {q['text'][:30]}...": q for i, q in enumerate(questions)}
            selected_question_key = st.selectbox("Select Question", options=list(question_options.keys()))
            selected_question = question_options[selected_question_key] if selected_question_key else None
        else:
            st.warning("No questions available. Please add questions first.")
            selected_question = None
    
    with col4:
        st.subheader("🎮 Game Controls")
        
        if st.button("🎯 Set Question", disabled=not selected_question):
            if selected_question and selected_player_data and timer_duration > 0:
                session_id = game_manager.create_session(selected_question, timer_duration, selected_player_data)
                st.success("Game session created!")
                st.rerun()
            else:
                st.error("Please select question, players, and set timer")
        
        current_session_id = st.session_state.current_session_id
        session_active = (current_session_id and 
                         current_session_id in st.session_state.game_sessions and
                         st.session_state.game_sessions[current_session_id]['is_active'])
        
        col4a, col4b = st.columns(2)
        with col4a:
            if st.button("▶️ Start", disabled=not current_session_id or session_active):
                if current_session_id:
                    game_manager.start_session(current_session_id)
                    st.success("Game started!")
                    st.rerun()
        
        with col4b:
            if st.button("⏹️ Stop", disabled=not session_active):
                if current_session_id:
                    game_manager.stop_session(current_session_id)
                    st.success("Game stopped!")
                    st.rerun()
        
        if st.button("📊 Evaluate", disabled=not current_session_id):
            evaluate_game_session(current_session_id)

def display_all_player_prompts(session_id, session_data):
    """Display all player prompt areas for admin monitoring"""
    selected_players = session_data['selected_players']
    
    cols = st.columns(min(len(selected_players), 3))  # Max 3 columns
    
    for i, player in enumerate(selected_players):
        col_idx = i % len(cols)
        with cols[col_idx]:
            st.write(f"**{player['fullname']}**")
            
            # Get current prompt
            current_prompt = session_data['player_prompts'].get(player['user_id'], '')
            
            # Display prompt (read-only for admin)
            st.text_area(
                f"Prompt for {player['fullname']}",
                value=current_prompt,
                height=150,
                disabled=True,
                key=f"admin_view_{player['user_id']}"
            )

def display_player_prompt_area(session_id):
    """Display prompt area for individual player"""
    user_id = st.session_state.user_data['user_id']
    session_data = st.session_state.game_sessions[session_id]
    
    # Check if current user is in selected players
    is_selected = any(player['user_id'] == user_id for player in session_data['selected_players'])
    
    if is_selected:
        current_prompt = session_data['player_prompts'].get(user_id, '')
        
        # Disable editing if game is not active
        disabled = not session_data['is_active']
        
        new_prompt = st.text_area(
            f"Your Prompt ({st.session_state.user_data['fullname']})",
            value=current_prompt,
            height=200,
            disabled=disabled,
            help="Enter your response to the question above" if not disabled else "Game is not active"
        )
        
        # Update prompt if changed and game is active
        if new_prompt != current_prompt and session_data['is_active']:
            st.session_state.game_sessions[session_id]['player_prompts'][user_id] = new_prompt
            st.rerun()
    else:
        st.warning("You are not selected for this game session.")

def display_timer(timer_placeholder, session_data):
    """Display and update timer"""
    if session_data['end_time']:
        remaining_time = session_data['end_time'] - datetime.now()
        
        if remaining_time.total_seconds() > 0:
            minutes = int(remaining_time.total_seconds() // 60)
            seconds = int(remaining_time.total_seconds() % 60)
            
            with timer_placeholder.container():
                st.markdown(f"""
                <div style="text-align: center; font-size: 2em; color: #ff6b6b; font-weight: bold;">
                    ⏰ {minutes:02d}:{seconds:02d}
                </div>
                """, unsafe_allow_html=True)
            
            # Auto-refresh every second
            time.sleep(1)
            st.rerun()
        else:
            # Time's up
            with timer_placeholder.container():
                st.markdown("""
                <div style="text-align: center; font-size: 2em; color: #ff0000; font-weight: bold;">
                    ⏰ TIME'S UP!
                </div>
                """, unsafe_allow_html=True)
            
            # Auto-stop the game
            st.session_state.game_sessions[st.session_state.current_session_id]['is_active'] = False

def evaluate_game_session(session_id):
    """Evaluate current game session"""
    if session_id in st.session_state.game_sessions:
        session_data = st.session_state.game_sessions[session_id]
        question = session_data['question']['text']
        prompts = {}
        
        # Get player names for prompts
        for player in session_data['selected_players']:
            player_id = player['user_id']
            player_name = player['fullname']
            prompt = session_data['player_prompts'].get(player_id, '')
            if prompt.strip():  # Only include non-empty prompts
                prompts[player_name] = prompt
        
        if prompts:
            # Evaluate prompts
            evaluation = LLMEvaluator.evaluate_prompts(question, prompts)
            
            # Save results
            result = {
                'session_id': session_id,
                'question': question,
                'prompts': prompts,
                'evaluation': evaluation,
                'timestamp': datetime.now().isoformat()
            }
            
            results = DataManager.load_results()
            results.append(result)
            DataManager.save_results(results)
            
            # Display evaluation
            st.success("Evaluation completed!")
            
            with st.expander("📊 Evaluation Results", expanded=True):
                if isinstance(evaluation, list):
                    st.subheader("🏆 Leaderboard")
                    eval_df = pd.DataFrame(evaluation)
                    st.dataframe(eval_df, use_container_width=True)
                    
                    # Highlight winner
                    if len(evaluation) > 0:
                        winner = evaluation[0]
                        st.balloons()
                        st.success(f"🎉 Winner: **{winner['player']}** with score {winner['total_score']}/10!")
                else:
                    st.write(evaluation)
        else:
            st.warning("No prompts to evaluate. Players need to submit their responses first.")

def main():
    """Main application function"""
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        if st.session_state.logged_in:
            st.write(f"👋 Logged in as: **{st.session_state.user_type.title()}**")
            if st.session_state.user_type == 'player':
                st.write(f"Name: {st.session_state.user_data['fullname']}")
            
            if st.button("🚪 Logout"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            st.write("Please log in to continue")
    
    # Main content
    if not st.session_state.logged_in:
        login_page()
    elif st.session_state.current_page == 'dashboard' and st.session_state.user_type == 'admin':
        admin_dashboard()
    elif st.session_state.current_page == 'playground':
        playground_page()
    else:
        st.error("Invalid page or insufficient permissions")

if __name__ == "__main__":
    main()
