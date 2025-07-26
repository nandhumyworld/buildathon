# requirements.txt
streamlit==1.28.1
pandas==2.0.3
uuid

# setup_instructions.md

# Prompt Battle Playground - Streamlit Setup Instructions

## Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

## Installation Steps

1. **Create a new directory for the project:**
   ```bash
   mkdir prompt_battle_playground
   cd prompt_battle_playground
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required packages:**
   ```bash
   pip install streamlit pandas
   ```

4. **Create the main application file:**
   - Save the Streamlit application code as `app.py`

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

6. **Access the application:**
   - Open your web browser
   - Navigate to `http://localhost:8501`

## File Structure
After setup, your directory should look like this:
```
prompt_battle_playground/
├── app.py                 # Main Streamlit application
├── admin_data.json        # Generated automatically (admin and user data)
├── results.json          # Generated automatically (game results)
├── users.csv             # Generated automatically (sample user data)
└── venv/                 # Virtual environment (if created)
```

## Default Login Credentials

### Admin Login:
- Email: `admin@example.com`
- Password: `admin123`

### Sample Player Logins:
- Email: `john@example.com`, Password: `1234567890`
- Email: `jane@example.com`, Password: `0987654321`
- Email: `alice@example.com`, Password: `1122334455`
- Email: `bob@example.com`, Password: `9988776655`
- Email: `charlie@example.com`, Password: `5566778899`

## Features Included

### Admin Features:
1. **User Management:**
   - Import users from CSV
   - View all registered users
   - Automatic CSV template creation

2. **Question Management:**
   - Add new questions
   - View existing questions
   - Question storage in JSON format

3. **Game Control:**
   - Set timer (minutes and seconds)
   - Select players for each game
   - Choose questions from the question bank
   - Start/Stop game sessions
   - Real-time monitoring of player prompts
   - Evaluate player responses with scoring

4. **Results