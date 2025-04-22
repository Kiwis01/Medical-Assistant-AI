import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from agents.superior_agent import SuperiorAgent
from config.config import Config
from utils.common_utils import *
from utils.imports import *

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'utils', 'images', 'uploads')
GENERATED_FOLDER = os.path.join(os.path.dirname(__file__), 'utils', 'images', 'generated')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

config = Config()
superior_agent = SuperiorAgent(config)

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