"use client";

import { useEffect, useState } from "react";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { useRouter } from "next/navigation";


export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  useEffect(() => {
    const user = localStorage.getItem("user");
    if (!user) {
      router.push("/login");
    }
  }, []);

  const handleSubmit = async (e: any) => {
    e.preventDefault();

    try {
      const res = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.message);
        return;
      }

      // Simpan user login
      localStorage.setItem("user", JSON.stringify(data.user));

      // REDIRECT KE CHAT
      router.push("/chat");

    } catch (error) {
      alert("Backend tidak terhubung");
    }
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
