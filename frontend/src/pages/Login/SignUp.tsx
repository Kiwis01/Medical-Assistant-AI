// src/SignUp.tsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.css";
import { API_BASE_URL } from "../../constants";

const SignUp: React.FC = () => {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [userType, setUserType] = useState<"patient" | "technician">("patient");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = {
      username,
      email,
      password,
      user_type: userType,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("");
        // After successful signup, redirect to signin page
        navigate("/signin");
      } else {
        setMessage(data.error || "Sign up failed");
      }
    } catch (error) {
      setMessage("An error occurred while signing up.");
      console.error(error);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Sign up</h2>
        <p className="subtitle">
          Create an account or <Link to="/signin">Sign in</Link>
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="email">Email address</label>
          <input
            type="email"
            id="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

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

          <label htmlFor="userType">I am a</label>
          <select
            id="userType"
            value={userType}
            onChange={(e) =>
              setUserType(e.target.value as "patient" | "technician")
            }
            required
            className="dropdown-spacing"
          >
            <option value="patient">Patient</option>
            <option value="technician">Technician</option>
          </select>

          <button type="submit">Sign up</button>
        </form>

        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
};

export default SignUp;
