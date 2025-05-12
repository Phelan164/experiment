"use client";

import { useState, useRef, FormEvent } from "react";

interface Message {
  sender: "user" | "bot";
  text: string;
}

const CHAT_API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || "http://localhost:8001/api/chat";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage: Message = { sender: "user", text: input };
    setMessages((msgs) => [...msgs, userMessage]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(CHAT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      if (!res.body) throw new Error("No response body");
      const reader = res.body.getReader();
      let botMessage = "";
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += new TextDecoder().decode(value);
        let boundary = buffer.indexOf("}\n");
        while (boundary !== -1) {
          const jsonStr = buffer.slice(0, boundary + 1);
          buffer = buffer.slice(boundary + 2);
          try {
            const data = JSON.parse(jsonStr);
            if (data.message) {
              botMessage += data.message;
            }
          } catch {}
          boundary = buffer.indexOf("}\n");
        }
      }
      // Try to parse any remaining buffer (for single JSON object)
      if (buffer.trim()) {
        try {
          const data = JSON.parse(buffer.trim());
          if (data.message) {
            botMessage += data.message;
          }
        } catch {}
      }
      setMessages((msgs) => [
        ...msgs,
        { sender: "bot", text: botMessage || "(No response)" },
      ]);
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { sender: "bot", text: "Error contacting backend." },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Music Instrument Chatbot</h2>
      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: 8,
          padding: 16,
          minHeight: 300,
          background: "#fafafa",
          marginBottom: 16,
          overflowY: "auto",
          height: 400,
        }}
      >
        {messages.length === 0 && (
          <div style={{ color: "#888" }}>Start the conversation...</div>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              textAlign: msg.sender === "user" ? "right" : "left",
              margin: "8px 0",
            }}
          >
            <span
              style={{
                display: "inline-block",
                background: msg.sender === "user" ? "#d1e7dd" : "#e2e3e5",
                color: "#222",
                borderRadius: 16,
                padding: "8px 16px",
                maxWidth: "80%",
                wordBreak: "break-word",
              }}
            >
              {msg.text}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={sendMessage} style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          style={{ flex: 1, padding: 8, borderRadius: 8, border: "1px solid #ccc" }}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{ padding: "8px 16px", borderRadius: 8, border: "none", background: "#0070f3", color: "#fff" }}
        >
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}
