// src/SignIn.tsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../services/auth";
import "./Auth.css";

const SignIn: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth(); // Move the hook to component level

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Use the login function from the useAuth hook
      const success = await login({
        username,
        password,
      });

      if (success) {
        setMessage("Login successful! Redirecting...");
        console.log("Login successful, redirecting to /chatbot");
        // Add a slight delay to ensure the state is updated
        setTimeout(() => {
          navigate("/chatbot");
        }, 500);
      } else {
        setMessage("Invalid username or password");
      }
    } catch (error) {
      setMessage("An error occurred while signing in.");
      console.error(error);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Sign in</h2>
        <p className="subtitle">
          Sign in to your account or <Link to="/">Sign up</Link>
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit">Sign in</button>
        </form>

        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
};

export default SignIn;
