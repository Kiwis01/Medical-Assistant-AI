# Medical Assistant AI - Backend

## Technical Overview
The backend is built on Flask and implements a multi-agent architecture powered by Google's Gemini LLM. Each agent specializes in a specific medical domain and provides tailored responses to user queries.

## Backend Architecture

### Agent System
The system uses a hierarchical agent architecture:

1. **Superior Agent**: Routes queries to specialized agents based on medical domain
2. **Specialist Agents**: Domain-specific agents (cardiology, neurology, etc.)
3. **Agent Tools**: Specialized capabilities for each agent (research, image analysis, etc.)

### Directory Structure
```
backend/
├── agent_tools/          # Specialized tools for each agent
├── agents/              # Agent implementations (cardiology, neurology, etc.)
├── config/              # Configuration files
├── llm/                 # LLM integration (Gemini)
├── rag/                 # Retrieval Augmented Generation components
├── utils/               # Shared utilities
├── app.py              # Main Flask application
├── main.py             # Entry point
└── requirements.txt    # Dependencies
```

## API Endpoints

### Authentication
- `POST /signup`: Register a new user
- `POST /signin`: Authenticate a user

### Chat
- `POST /chat`: Send a query to the medical assistant

### Image Processing
- `POST /upload`: Upload a medical image
- `GET /uploads/<filename>`: Retrieve an uploaded image
- `GET /generated/<filename>`: Retrieve a generated image with annotations

### System
- `GET /health`: Check API health status

## Development Guidelines

### Adding a New Agent
1. Create a new agent class in `agents/` that extends `BaseAgent`
2. Implement the `handle_query` method
3. Add specialized tools in `agent_tools/` if needed
4. Register the agent in `SuperiorAgent.__init__`

### Path Structure
The application uses a consistent path structure for file management:
- Uploaded images: `app.config['UPLOAD_FOLDER']`
- Generated images: `app.config['GENERATED_FOLDER']`

## Technical Implementation Details

### Conversation History Management
The system currently maintains conversation history by appending messages to a list. Future improvements could include:

1. **Summarization-Based Context**: Periodically summarize older parts of the conversation
2. **Semantic Search with Embeddings**: Use embeddings to retrieve only relevant past messages
3. **Medical-Specific Context**: Organize context by medical conditions and symptoms

### Image Processing Pipeline
1. Image upload through the `/upload` endpoint
2. Analysis using specialized agent tools
3. Annotation and visualization of results
4. Caching of predictions for improved performance
