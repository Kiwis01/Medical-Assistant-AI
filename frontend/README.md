# Medical Assistant AI - Frontend

## Overview
The frontend of the Medical Assistant AI is a React-based web application built with TypeScript. It provides an intuitive interface for users to interact with the AI medical assistant, upload medical images, and receive specialized medical insights.

## Features

- **Interactive Chat Interface**: Communicate with specialized medical agents
- **Image Upload**: Submit medical images for AI analysis
- **Authentication System**: Secure login and registration
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Feedback**: Immediate responses from the AI system

## Tech Stack

- **Framework**: React 19 with TypeScript
- **Routing**: React Router v7
- **UI Components**: Custom components with React Icons
- **Markdown Rendering**: React Markdown for formatted responses
- **Authentication**: Custom auth service with JWT

## Project Structure

```
frontend/
├── public/              # Static files
├── src/                 # Source code
│   ├── pages/           # Application pages
│   │   ├── Chatbot/     # Chat interface components
│   │   └── Login/       # Authentication components
│   ├── services/        # API and auth services
│   ├── App.tsx          # Main application component
│   └── index.tsx        # Application entry point
├── package.json         # Dependencies and scripts
└── tsconfig.json        # TypeScript configuration
```

## Development

### Prerequisites
- Node.js 16+ and npm

### Available Scripts

#### `npm start`
Runs the app in development mode at [http://localhost:3000](http://localhost:3000).

#### `npm test`
Launches the test runner in interactive watch mode.

#### `npm run build`
Builds the app for production to the `build` folder.

### Connecting to Backend

The frontend communicates with the backend through API endpoints. The main interaction points are:

- **Authentication**: Login and registration
- **Chat**: Sending queries and receiving responses
- **Image Upload**: Submitting medical images for analysis

All API calls are configured to connect to the backend running at `http://localhost:5000` by default.

## UI Components

### Chat Interface
The chat interface allows users to:
- Send text queries to the medical assistant
- Upload medical images for analysis
- View AI-generated responses with proper formatting
- See annotated medical images with diagnostic overlays

### Authentication
The authentication system provides:
- User registration with role selection (patient/technician)
- Secure login with JWT token storage
- Protected routes for authenticated users

## Extending the Frontend

### Adding New Pages
1. Create a new directory in `src/pages/`
2. Implement your React components
3. Add the route in `App.tsx`

### Styling Guidelines
The application uses a consistent styling approach with:
- Responsive design principles
- Accessible UI elements
- Consistent color scheme for medical context
