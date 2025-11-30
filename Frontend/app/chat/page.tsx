"use client";

import { useState } from "react";
import { chatSuggestions, chatHistoryDummy } from "./data";
import { SendOutlined } from "@ant-design/icons";

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState(chatHistoryDummy);

  const sendMessage = () => {
    if (!input.trim()) return;

    setMessages((prev) => [
      ...prev,
      { sender: "user", message: input }
    ]);

    setInput("");

    // Dummy bot reply
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", message: "Ini hanya respon dummy ya..." }
      ]);
    }, 400);
  };

  return (
    <div className="chat-root">
      <h1 className="chat-title">Hii, apa yang bisa saya bantu ?</h1>

      {/* Suggestions */}
      <div className="suggestions-container">
        {chatSuggestions.map((text, i) => (
          <button
            key={i}
            className="suggestion-pill"
            onClick={() => setInput(text)}
          >
            {text}
          </button>
        ))}
      </div>

      {/* Messages (optional) */}
      <div className="chat-box">
        {messages.map((m, i) => (
          <div
            key={i}
            className={m.sender === "user" ? "chat-user" : "chat-bot"}
          >
            {m.message}
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="chat-input-wrapper">
        <input
          className="chat-input"
          placeholder="Silahkan tanya gejala penyakit anda"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button className="chat-send-btn" onClick={sendMessage}>
          <SendOutlined />
        </button>
      </div>
    </div>
  );
}
