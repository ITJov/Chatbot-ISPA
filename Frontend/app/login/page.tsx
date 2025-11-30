"use client";

import { useState } from "react";
import { UserOutlined, LockOutlined } from "@ant-design/icons";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: any) => {
    e.preventDefault();
    console.log("Login with:", { username, password });
  };

  return (
    <div className="login-root">
      <div className="login-card">
        <h1 className="login-title">Login Page</h1>

        <form className="login-form" onSubmit={handleSubmit}>
          {/* Username */}
          <div className="input-group">
            <UserOutlined className="input-icon" />
            <input
              className="input-field"
              type="text"
              placeholder="USERNAME"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
          </div>

          {/* Password */}
          <div className="input-group">
            <LockOutlined className="input-icon" />
            <input
              className="input-field"
              type="password"
              placeholder="PASSWORD"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="login-button">
            Login
          </button>
        </form>

        <div className="forgot-wrapper">
          <a href="#" className="forgot-link">
            Forgot password?
          </a>
        </div>
      </div>
    </div>
  );
}
