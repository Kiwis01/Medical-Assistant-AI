import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from agents.superior_agent import SuperiorAgent
from config.config import Config
from utils.common_utils import *
from utils.imports import *
from utils.models import db, User    


# initialize flask app
app = Flask(__name__)
CORS(app)
config = Config()

# important paths and constants
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'utils', 'images', 'uploads')
GENERATED_FOLDER = os.path.join(os.path.dirname(__file__), 'utils', 'images', 'generated')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
VALID_USER_TYPES = ['patient', 'technician']

# Flask image and file folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = config.database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Gemini activation of superior agent
superior_agent = SuperiorAgent(config)

# Initialize DB 
db.init_app(app)

# Create tables if not exist
with app.app_context():
    db.create_all()

# sign up routes
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('user_type')

    if not (username and email and password and user_type):
        return jsonify(error="Missing required fields"), 400

    if user_type not in VALID_USER_TYPES:
        return jsonify(error="Invalid user_type"), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify(error="Username or email already exists"), 400

    user = User(
        username=username, 
        email=email, 
        password_hash=generate_password_hash(password), 
        user_type=user_type
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(message="User created successfully"), 201

# sign in routes
@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(error="Missing username or password"), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify(error="Invalid username or password"), 401

    return jsonify(
        message="Signed in successfully",
        user_type=user.user_type
    ), 200

# Optionally: Use a simple in-memory store for conversation histories keyed by session/user_id (for demo)
# For production, use a DB or persistent store
conversation_histories = {}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Return the relative path to the frontend
        return jsonify({'image_path': f'/uploads/{filename}'}), 200
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/generated/<filename>')
def generated_file(filename):
    return send_from_directory(GENERATED_FOLDER, filename)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(force=True)
    query = data.get('query', '')
    user_id = data.get('user_id', 'default')
    history = data.get('history', [])  # List of {role, text}

    # Track conversation history for this user/session
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []
    conversation_history = conversation_histories[user_id]

    # Add user input
    conversation_history.append({"role": "user", "text": query})

    # Determine specialty and route
    specialty = superior_agent.determine_specialty(query)
    if specialty:
        agent = superior_agent.specialist_agents.get(specialty)
        if agent:
                response = agent.handle_query(conversation_history)
                conversation_history.append({"role": "model", "agent": specialty, "text": response})
                result = {"response": response, "history": conversation_history, "specialty": specialty}
        else:
            config.logger.warning(f"@app.py No specialist agent found, {specialty}")
            conversation_history.append({"role": "model", "agent": None, "text": specialty})
            result = {"response": specialty, "history": conversation_history, "specialty": specialty}
    else:
        config.logger.warning("@app.py Could not determine specialty.")
        conversation_history.append({"role": "model", "agent": None, "text": "Could not determine specialty."})
        result = {"response": "Could not determine specialty.", "history": conversation_history, "specialty": None}

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)