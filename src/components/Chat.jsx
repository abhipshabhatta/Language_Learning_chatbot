import React, { useState } from 'react';
import axios from 'axios';
import './Chat.css';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const [language, setLanguage] = useState(''); // for new selected language


  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!input.trim()) {
      setError('Please enter a valid question.');
      return;
    }

    if (!language.trim()) {
      setError('Please select a language to learn.');
      return;
    }

    setError('');

    const newMessage = { sender: 'user', text: input };
    setMessages([...messages, newMessage]);

    try {
      const response = await axios.post('http://localhost:5000/chat/ask', { question: `${language}: ${input}` }, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.status === 200) {
        const aiMessage = { sender: 'ai', text: response.data.answer };
        setMessages((prevMessages) => [...prevMessages, aiMessage]);
      }
    } catch (error) {
      console.error("Error fetching AI response:", error);
      setError('An error occurred while trying to get a response. Please try again.');
    }

    setInput('');
  };

  return (
    <div className="chat-container">
      <h2>Chat with Your Language Tutor</h2>
      <div className="language-selection">
        <label>Select a language to learn:</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)} required>
          <option value="">--Select a Language--</option>
          <option value="French">French</option>
          <option value="Spanish">Spanish</option>
          <option value="German">German</option>
          <option value="Japanese">Japanese</option>
        </select>
      </div>
      <div className="chat-box">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender === 'user' ? 'user-message' : 'ai-message'}`}>
            <p>{message.text}</p>
          </div>
        ))}
      </div>
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about language you want to learn"
          required
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default Chat;
