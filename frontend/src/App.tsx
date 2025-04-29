// src/App.tsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import SignIn from './pages/Login/SignIn';
import SignUp from './pages/Login/SignUp';
import Dashboard from './pages/Login/Dashboard';
import Chatbot from './pages/Chatbot';
import { useAuth } from './services/auth';

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route 
          path="/chatbot" 
          element={isAuthenticated ? <Chatbot /> : <Navigate to="/signin" />} 
        />
        <Route path="/" element={<Navigate to={isAuthenticated ? "/chatbot" : "/signup"} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;