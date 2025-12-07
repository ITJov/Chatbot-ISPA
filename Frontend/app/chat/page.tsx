"use client";

import { useState, useEffect } from "react";
import { SendOutlined } from "@ant-design/icons";
import { chatSuggestions, chatHistoryDummy } from "./data";
import DiagnosisResult from "../components/DiagnosisResult";

type Message = {
  sender: "user" | "bot";
  message: string;
};

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>(
    (chatHistoryDummy as Message[]) || []
  );

  const [userSentCount, setUserSentCount] = useState(0);
  const [showDiagnosis, setShowDiagnosis] = useState(false);

  const sidebarItems = [
    {
      title: "Gejala batuk berat",
      desc: "Merasakan nyeri dada yang tak tertahankan...",
    },
    {
      title: "Demam tinggi",
      desc: "Suhu badan di atas 38°C selama 3 hari...",
    },
    {
      title: "Sesak napas",
      desc: "Sulit bernapas saat beraktivitas ringan...",
    },
  ];
  const [activeSidebar, setActiveSidebar] = useState(0);

  const sendMessage = () => {
    if (!input.trim()) return;

    const text = input.trim();

    setMessages((prev) => [...prev, { sender: "user", message: text }]);
    setInput("");
    setUserSentCount((c) => c + 1);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          message:
            "Oh baik, ini hanya respon dummy ya. Nanti bakal dihubungkan ke model / backend.",
        },
      ]);
    }, 500);
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  };

  // ✅ setelah user kirim 5x pesan, tampilkan hasil diagnosa (tanpa pindah halaman)
  useEffect(() => {
    if (userSentCount >= 5 && !showDiagnosis) {
      setShowDiagnosis(true);
    }
  }, [userSentCount, showDiagnosis]);

  return (
    <div className="w-screen h-screen flex items-stretch justify-center bg-gradient-to-br from-[#f7f4ff] via-[#e4e9ff] to-[#f8fbff]">
      <div className="w-full h-full bg-white/70 backdrop-blur-xl shadow-2xl lg:rounded-3xl overflow-hidden flex">
        {/* SIDEBAR */}
        <aside className="w-64 h-full bg-white/90 border-r border-white/70 p-5 flex flex-col gap-4">
          <div className="flex justify-end">
            <button className="text-gray-500 hover:text-gray-700 text-xl">
              ✕
            </button>
          </div>

          <h2 className="text-sm font-semibold text-gray-500">Riwayat Gejala</h2>

          <div className="flex flex-col gap-3 mt-1">
            {sidebarItems.map((item, i) => (
              <button
                key={i}
                onClick={() => setActiveSidebar(i)}
                className={`w-full text-left p-3 rounded-2xl transition border
                  ${
                    activeSidebar === i
                      ? "bg-indigo-100 border-indigo-300"
                      : "bg-indigo-50/60 hover:bg-indigo-100 border-transparent"
                  }`}
              >
                <div className="font-semibold text-gray-800 text-sm">
                  {item.title}
                </div>
                <div className="text-xs text-gray-500 truncate">
                  {item.desc}
                </div>
              </button>
            ))}
          </div>
        </aside>

        {/* MAIN CHAT */}
        <main className="flex-1 h-full flex flex-col p-10 bg-gradient-to-b from-[#f9f7ff] via-[#f1f2ff] to-[#e4ebff]">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="text-indigo-300 text-xl tracking-[0.4em] mb-2">
              ✦✦✦
            </div>
            <h1 className="text-xl md:text-2xl font-medium text-gray-800">
              Hii, apa yang bisa saya bantu ?
            </h1>
          </div>

          {/* Suggestions */}
          <div className="flex justify-center flex-wrap gap-3 mb-6">
            {chatSuggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => setInput(s)}
                className="px-4 py-2 bg-white shadow-md text-xs rounded-full 
                  hover:shadow-lg transition text-gray-600"
              >
                {s}
              </button>
            ))}
          </div>

          {/* Chat messages + hasil diagnosa di dalam area scroll */}
          <div className="flex-1 overflow-y-auto pr-3 space-y-5 pb-8">
            {messages.map((m, i) => (
              <div key={i}>
                <div className="text-[10px] text-gray-400 font-semibold mb-1 uppercase tracking-wide">
                  {m.sender === "user" ? "NATHANIEL VALENTINO R" : "AI CHATBOT"}
                </div>
                <div
                  className={`inline-block px-4 py-3 rounded-2xl text-sm shadow-md
                    ${
                      m.sender === "user"
                        ? "bg-white text-gray-800"
                        : "bg-indigo-100 text-gray-800"
                    }`}
                >
                  {m.message}
                </div>
              </div>
            ))}

            {showDiagnosis && (
              <div className="mt-8">
                <DiagnosisResult />
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t border-white/60 pt-4 flex items-center gap-3 mt-3">
            <input
              className="flex-1 px-4 py-3 bg-white/90 border border-indigo-200 
                rounded-full text-sm outline-none focus:ring-2 focus:ring-indigo-300"
              placeholder="Silahkan tanya gejala penyakit anda"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />

            <button
              onClick={sendMessage}
              className="w-11 h-11 rounded-full bg-indigo-300 text-white shadow-lg 
                hover:bg-indigo-400 transition flex items-center justify-center"
            >
              <SendOutlined />
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}