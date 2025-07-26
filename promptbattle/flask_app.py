from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import csv
import os
from datetime import datetime
import openai
from werkzeug.security import check_password_hash, generate_password_hash
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# File paths
ADMIN_DATA_FILE = 'admin_data.json'
RESULTS_FILE = 'results.json'
USERS_CSV_FILE = 'users.csv'

# OpenAI API key (set your API key)
# openai.api_key = 'your-openai-api-key'

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
    def import_users_from_csv():
        """Import users from CSV file"""
        admin_data = DataManager.load_admin_data()
        users = []
        
        if os.path.exists(USERS_CSV_FILE):
            with open(USERS_CSV_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user = {
                        'user_id': row['user_id'],
                        'fullname': row['fullname'],
                        'emailid': row['emailid'],
                        'phonenumber': row['phonenumber'],
                        'is_technical': row['IsTechnical'].lower() == 'yes',
                        'password': row['phonenumber']  # Default password is phone number
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
        self.active_sessions = {}
        self.player_prompts = {}
    
    def create_session(self, session_id, question, timer_duration, selected_players):
        """Create a new game session"""
        self.active_sessions[session_id] = {
            'question': question,
            'timer_duration': timer_duration,
            'selected_players': selected_players,
            'is_active': False,
            'start_time': None,
            'player_prompts': {}
        }
    
    def start_session(self, session_id):
        """Start a game session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['is_active'] = True
            self.active_sessions[session_id]['start_time'] = datetime.now()
    
    def stop_session(self, session_id):
        """Stop a game session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['is_active'] = False
    
    def update_player_prompt(self, session_id, player_id, prompt):
        """Update player's prompt"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['player_prompts'][player_id] = prompt

game_manager = GameManager()

class LLMEvaluator:
    """Handles LLM evaluation using OpenAI"""
    
    @staticmethod
    def evaluate_prompts(question, prompts):
        """Evaluate prompts using OpenAI LLM"""
        try:
            # Prepare evaluation prompt
            evaluation_prompt = f"""
            Question: {question}
            
            Please evaluate the following prompts and provide analysis:
            
            """
            
            for i, (player, prompt) in enumerate(prompts.items(), 1):
                evaluation_prompt += f"Player {i} ({player}): {prompt}\n"
            
            evaluation_prompt += "\nProvide detailed analysis of each prompt's effectiveness, creativity, and relevance to the question."
            
            # Note: Uncomment and configure when you have OpenAI API key
            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "system", "content": "You are an expert prompt evaluator."},
            #         {"role": "user", "content": evaluation_prompt}
            #     ]
            # )
            # 
            # return response.choices[0].message.content
            
            # Mock response for demonstration
            return f"Mock evaluation for question: {question}\nPrompts evaluated: {len(prompts)}"
            
        except Exception as e:
            return f"Error in evaluation: {str(e)}"

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/admin-login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    email = request.json.get('email')
    password = request.json.get('password')
    
    admin = UserManager.authenticate_admin(email, password)
    
    if admin:
        session['user_type'] = 'admin'
        session['user_email'] = email
        return jsonify({'success': True, 'redirect': '/admin-dashboard'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/player-login', methods=['POST'])
def player_login():
    """Player login endpoint"""
    email = request.json.get('email')
    password = request.json.get('password')
    
    user = UserManager.authenticate_user(email, password)
    
    if user:
        session['user_type'] = 'player'
        session['user_email'] = email
        session['user_id'] = user['user_id']
        session['user_name'] = user['fullname']
        return jsonify({'success': True, 'redirect': '/playground'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/admin-dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if session.get('user_type') != 'admin':
        return redirect(url_for('login_page'))
    
    users = UserManager.get_all_users()
    questions = QuestionManager.get_all_questions()
    
    return render_template('admin_dashboard.html', users=users, questions=questions)

@app.route('/playground')
def playground():
    """Main playground page"""
    if 'user_type' not in session:
        return redirect(url_for('login_page'))
    
    return render_template('playground.html', 
                         user_type=session.get('user_type'),
                         user_name=session.get('user_name', ''))

@app.route('/import-users', methods=['POST'])
def import_users():
    """Import users from CSV"""
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        users = UserManager.import_users_from_csv()
        return jsonify({'success': True, 'message': f'Imported {len(users)} users'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/add-question', methods=['POST'])
def add_question():
    """Add new question"""
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    question_text = request.json.get('question')
    
    if question_text:
        question = QuestionManager.add_question(question_text)
        return jsonify({'success': True, 'question': question})
    else:
        return jsonify({'success': False, 'message': 'Question text required'})

@app.route('/get-questions')
def get_questions():
    """Get all questions"""
    questions = QuestionManager.get_all_questions()
    return jsonify({'questions': questions})

@app.route('/get-users')
def get_users():
    """Get all users"""
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    users = UserManager.get_all_users()
    return jsonify({'users': users})

@app.route('/start-game', methods=['POST'])
def start_game():
    """Start game session"""
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    session_id = str(uuid.uuid4())
    
    question_id = data.get('question_id')
    timer_duration = data.get('timer_duration')
    selected_players = data.get('selected_players', [])
    
    question = QuestionManager.get_question_by_id(question_id)
    
    if question:
        game_manager.create_session(session_id, question, timer_duration, selected_players)
        game_manager.start_session(session_id)
        
        # Emit game start to all clients
        socketio.emit('game_started', {
            'session_id': session_id,
            'question': question['text'],
            'timer_duration': timer_duration
        })
        
        return jsonify({'success': True, 'session_id': session_id})
    else:
        return jsonify({'success': False, 'message': 'Question not found'})

@app.route('/stop-game', methods=['POST'])
def stop_game():
    """Stop game session"""
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    session_id = request.json.get('session_id')
    
    if session_id:
        game_manager.stop_session(session_id)
        socketio.emit('game_stopped', {'session_id': session_id})
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Session ID required'})

@app.route('/evaluate-prompts', methods=['POST'])
def evaluate_prompts():
    """Evaluate prompts using LLM"""
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    session_id = request.json.get('session_id')
    
    if session_id in game_manager.active_sessions:
        session_data = game_manager.active_sessions[session_id]
        question = session_data['question']['text']
        prompts = session_data['player_prompts']
        
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
        
        return jsonify({'success': True, 'evaluation': evaluation})
    else:
        return jsonify({'success': False, 'message': 'Session not found'})

# WebSocket events
@socketio.on('join_room')
def on_join(data):
    """Handle user joining room"""
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'{session.get("user_name", "User")} has entered the room.'}, room=room)

@socketio.on('leave_room')
def on_leave(data):
    """Handle user leaving room"""
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'{session.get("user_name", "User")} has left the room.'}, room=room)

@socketio.on('update_prompt')
def handle_prompt_update(data):
    """Handle real-time prompt updates"""
    session_id = data.get('session_id')
    player_id = session.get('user_id')
    prompt = data.get('prompt', '')
    
    if session_id and player_id:
        game_manager.update_player_prompt(session_id, player_id, prompt)
        
        # Emit to admin for real-time monitoring
        emit('prompt_updated', {
            'player_id': player_id,
            'player_name': session.get('user_name'),
            'prompt': prompt
        }, broadcast=True)

@socketio.on('timer_update')
def handle_timer_update(data):
    """Handle timer updates"""
    if session.get('user_type') == 'admin':
        emit('timer_sync', data, broadcast=True)

if __name__ == '__main__':
    # Create sample CSV file if it doesn't exist
    if not os.path.exists(USERS_CSV_FILE):
        with open(USERS_CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'fullname', 'emailid', 'phonenumber', 'IsTechnical'])
            writer.writerow(['1', 'Nandhu', 'nandhu@python.com', '0123456789', 'yes'])
            writer.writerow(['2', 'Jane', 'jane@python.com', '0123456789', 'no'])
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)