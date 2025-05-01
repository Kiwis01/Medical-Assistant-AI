# ⚕️ MedAssistAI 

MedAssistAI is an advanced medical assistant chatbot capable of handling symptom-related issues using a multi-agent AI architecture. The system leverages Google's Gemini LLM to provide specialized medical insights across different domains including cardiology, neurology, and general medicine.

## Features

- **Multi-Agent Architecture**: Routes queries to specialized medical agents based on symptoms
- **Image Analysis**: Processes medical images (such as MRIs, X-rays) for diagnosis assistance
- **Research Integration**: Retrieves relevant medical research for comprehensive responses
- **Conversation History**: Maintains context across user interactions
- **Caching System**: Optimizes performance by caching predictions and generated images

## Tech Stack

### Backend
- **Framework**: Flask
- **LLM**: Google Gemini 2.0 Flash
- **Database**: PostgreSQL with SQLAlchemy
- **Image Processing**: OpenCV

### Frontend
- **Framework**: React
- **UI Library**: Material UI
- **State Management**: React Context API

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js and npm
- PostgreSQL database
- Google Gemini API key

### Installation

You will need to run two terminals simultaneously:

#### Terminal 1 / Run Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Terminal 2 / Run Frontend
```bash
cd frontend
npm install
```

### Configuration
1. Create `backend/config/config.json` with your API keys and database settings (see `backend/config/sample_config.json` for an example)
2. Ensure the PostgreSQL database is created and accessible

## Usage

#### Terminal 1 / Start Backend Server
```bash
cd backend
python app.py
```

#### Terminal 2 / Start Frontend Development Server
```bash
cd frontend
npm start
```

The application will be available at http://localhost:3000

## Project Structure

```
Medical-Assistant-AI/
├── backend/           # Flask backend with multi-agent architecture
├── frontend/         # React frontend application
└── README.md         # This file
```

For more detailed information:
- [Backend Documentation](./backend/README.md)
- [Frontend Documentation](./frontend/README.md)

<!-- ## License
[Specify your license here] -->

## Contributors
Carlos Quihuis - chquihui@asu.edu
Jacob Swarzmiller - jswartzm@asu.edu
Vincent Nguyen - vnguye58@asu.edu
