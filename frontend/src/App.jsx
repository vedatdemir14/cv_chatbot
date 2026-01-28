import { useState, useEffect, useRef } from "react";
import "./App.css";

const STORAGE_KEY = "cv_chatbot_history";
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem(STORAGE_KEY);
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory);
        setMessages(parsed);
      } catch (e) {
        console.error("Error loading chat history:", e);
      }
    }
  }, []);

  // Save chat history to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    }
  }, [messages]);

  // Auto-scroll to bottom when new message arrives
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const askQuestion = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: userMessage.content }),
      });

      const data = await response.json();
      const botMessage = {
        role: "assistant",
        content: data.answer || "Sorry, I couldn't get a response.",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        role: "assistant",
        content: "❌ Backend is not reachable. Please make sure the server is running.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }

    setLoading(false);
  };

  const clearHistory = () => {
    if (window.confirm("Are you sure you want to clear chat history?")) {
      setMessages([]);
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString("tr-TR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="app-container">
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-content">
            <h1>AI CV Chatbot</h1>
            <p>Ask questions about my CV, skills, and projects</p>
          </div>
          {messages.length > 0 && (
            <button className="clear-btn" onClick={clearHistory} title="Clear chat history">
              Clear
            </button>
          )}
        </div>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <div className="welcome-icon">Hello</div>
              <h2>Welcome!</h2>
              <p>Start a conversation by asking a question about my CV, skills, or projects.</p>
              <div className="suggestions">
                <div className="suggestion-chip" onClick={() => setInput("What programming languages do you know?")}>
                  What programming languages do you know?
                </div>
                <div className="suggestion-chip" onClick={() => setInput("Tell me about your projects")}>
                  Tell me about your projects
                </div>
                <div className="suggestion-chip" onClick={() => setInput("What are your skills?")}>
                  What are your skills?
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-role">
                      {msg.role === "user" ? "You" : "Assistant"}
                    </span>
                    <span className="message-time">{formatTime(msg.timestamp)}</span>
                  </div>
                  <div className="message-text">{msg.content}</div>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="message-header">
                  <span className="message-role">Assistant</span>
                </div>
                <div className="message-text loading">
                  <span className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            placeholder="Type your question here... (Press Enter to send, Shift+Enter for new line)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            rows="2"
            disabled={loading}
          />
          <button
            className="send-btn"
            onClick={askQuestion}
            disabled={loading || !input.trim()}
          >
            {loading ? "…" : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
