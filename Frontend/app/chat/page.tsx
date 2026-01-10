"use client";

import { useState, useEffect, useRef } from "react";
import { SendOutlined, LoadingOutlined } from "@ant-design/icons";
import { chatSuggestions } from "./data";
import DiagnosisResult from "../components/DiagnosisResult";
import ListDokter from "../components/ListDokter";

type Message = {
  sender: "user" | "bot";
  message: string;
};

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [userSentCount, setUserSentCount] = useState(0);
  const [showDiagnosis, setShowDiagnosis] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // REFS
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  
  // 1. BUAT REF UNTUK MENYIMPAN SESSION ID
  const sessionIdRef = useRef(""); 

  const BACKEND_URL = "http://127.0.0.1:5000/chat"; 

  // ... (Sidebar Items sama seperti sebelumnya) ...
  const sidebarItems = [
    { title: "Gejala batuk berat", desc: "Merasakan nyeri dada..." },
    { title: "Demam tinggi", desc: "Suhu badan di atas 38°C..." },
    { title: "Sesak napas", desc: "Sulit bernapas saat beraktivitas..." },
  ];
  const [activeSidebar, setActiveSidebar] = useState(0);

  const scrollToBottom = (behavior: ScrollBehavior = "smooth") => {
    messagesEndRef.current?.scrollIntoView({ behavior, block: "end" });
  };

  // 2. GENERATE ID BARU SETIAP KALI HALAMAN DI-REFRESH
  useEffect(() => {
    // ID Unik: Waktu sekarang + Angka Acak
    const randomId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionIdRef.current = randomId;
    
    console.log("Session ID Baru:", sessionIdRef.current); // Cek di Console Browser
    scrollToBottom("auto");
  }, []); // [] artinya hanya jalan sekali pas halaman dimuat

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const text = input.trim();
    const newUserMessage: Message = { sender: "user", message: text };
    
    setMessages((prev) => [...prev, newUserMessage]);
    setInput("");
    setIsLoading(true);
    setUserSentCount((c) => c + 1);

    try {
      // 3. KIRIM SESSION ID KE BACKEND
      const response = await fetch(BACKEND_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
            message: text, 
            session_id: sessionIdRef.current // <--- INI KUNCINYA
        }), 
      });

      if (!response.ok) throw new Error("Gagal mengambil respon");

      const data = await response.json();
      const botResponse = data.response || "Maaf, saya tidak mengerti."; 
      
      setMessages((prev) => [
        ...prev,
        { sender: "bot", message: botResponse },
      ]);

    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", message: "Maaf, terjadi kesalahan koneksi ke server." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  };

  useEffect(() => {
    if (userSentCount >= 5 && !showDiagnosis) {
      setShowDiagnosis(true);
    }
  }, [userSentCount, showDiagnosis]);

  useEffect(() => {
    scrollToBottom("smooth");
  }, [messages, isLoading]);

  return (
    <div className="w-screen h-screen flex items-stretch justify-center bg-gradient-to-br from-[#f7f4ff] via-[#e4e9ff] to-[#f8fbff]">
      <div className="w-full h-full bg-white/70 backdrop-blur-xl shadow-2xl lg:rounded-3xl overflow-hidden flex">
        
        {/* SIDEBAR */}
        <aside className="w-64 h-full bg-white/90 border-r border-white/70 p-5 flex flex-col gap-4 hidden md:flex">
          <h2 className="text-sm font-semibold text-gray-500">Riwayat Gejala</h2>
          <div className="flex flex-col gap-3 mt-1">
            {sidebarItems.map((item, i) => (
              <button
                key={i}
                onClick={() => setActiveSidebar(i)}
                className={`w-full text-left p-3 rounded-2xl transition border
                  ${activeSidebar === i ? "bg-indigo-100 border-indigo-300" : "bg-indigo-50/60 hover:bg-indigo-100 border-transparent"}`}
              >
                <div className="font-semibold text-gray-800 text-sm">{item.title}</div>
                <div className="text-xs text-gray-500 truncate">{item.desc}</div>
              </button>
            ))}
          </div>
        </aside>

        {/* MAIN CHAT */}
        <main className="flex-1 h-full flex flex-col p-4 md:p-10 bg-gradient-to-b from-[#f9f7ff] via-[#f1f2ff] to-[#e4ebff]">
          <div className="text-center mb-6">
            <div className="text-indigo-300 text-xl tracking-[0.4em] mb-2">✦✦✦</div>
            <h1 className="text-xl md:text-2xl font-medium text-gray-800">Hii, apa yang bisa saya bantu ?</h1>
          </div>

          <div className="flex justify-center flex-wrap gap-3 mb-6">
            {chatSuggestions.map((s, i) => (
              <button key={i} onClick={() => setInput(s)} disabled={isLoading}
                className="px-4 py-2 bg-white shadow-md text-xs rounded-full hover:shadow-lg transition text-gray-600 disabled:opacity-50">
                {s}
              </button>
            ))}
          </div>

          <div ref={messagesContainerRef} className="flex-1 overflow-y-auto pr-3 space-y-5 pb-8 no-scrollbar">
            {messages.map((m, i) => (
              <div key={i}>
                <div className="text-[10px] text-gray-400 font-semibold mb-1 uppercase tracking-wide">
                  {m.sender === "user" ? "NATHANIEL VALENTINO R" : "AI CHATBOT"}
                </div>
                <div className={`inline-block px-4 py-3 rounded-2xl text-sm shadow-md whitespace-pre-wrap
                    ${m.sender === "user" ? "bg-white text-gray-800" : "bg-indigo-100 text-gray-800"}`}>
                  {m.message}
                </div>
              </div>
            ))}
            
            {isLoading && (
               <div className="text-gray-400 text-xs italic ml-2 animate-pulse">AI sedang berpikir...</div>
            )}

            {showDiagnosis && (
              <div className="mt-8"><DiagnosisResult /><ListDokter /></div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-white/60 pt-4 flex items-center gap-3 mt-3">
            <input
              className="flex-1 px-4 py-3 bg-white/90 border border-indigo-200 rounded-full text-sm outline-none focus:ring-2 focus:ring-indigo-300 disabled:bg-gray-100"
              placeholder={isLoading ? "Tunggu sebentar..." : "Silakan tanya gejala penyakit anda"}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading} 
            />
            <button onClick={sendMessage} disabled={isLoading}
              className={`w-11 h-11 rounded-full text-white shadow-lg transition flex items-center justify-center
                ${isLoading ? "bg-gray-400 cursor-not-allowed" : "bg-indigo-300 hover:bg-indigo-400"}`}>
              {isLoading ? <LoadingOutlined /> : <SendOutlined />}
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}