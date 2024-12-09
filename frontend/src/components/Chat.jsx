import React, { useState } from 'react';
import axios from 'axios';
import './Chat.css';

const Chat = () => {
    const [question, setQuestion] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [isTyping, setIsTyping] = useState(false);

    const handleAsk = async () => {
        if (!question.trim()) return;

        // Add user's question to chat history
        setChatHistory((prevHistory) => [
            ...prevHistory,
            { role: 'user', message: question },
        ]);
        setQuestion(''); // Clear input field
        setIsTyping(true); // Indicate bot is typing

        try {
            // Make the backend request
            const response = await axios.post(
                'http://127.0.0.1:5000/chat/ask',
                { question: question.trim() },
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('jwtToken')}`,
                    },
                }
            );

            const answer = response.data.answer?.trim() || ''; // Ensure no undefined or extra spaces
            simulateTyping(answer);
        } catch (error) {
            console.error(error);
            simulateTyping('An error occurred. Please try again.');
        }
    };

    const simulateTyping = (text) => {
        let index = 0;

        // Add an initial empty bot message to chat history
        setChatHistory((prevHistory) => [
            ...prevHistory,
            { role: 'bot', message: text[0] || '' }, // Initialize with the first character
        ]);

        // Typing simulation
        const interval = setInterval(() => {
            index++;

            setChatHistory((prevHistory) => {
                const lastMessage = prevHistory[prevHistory.length - 1];

                // Safeguard: Update only the last bot message
                if (lastMessage.role === 'bot') {
                    return [
                        ...prevHistory.slice(0, -1),
                        {
                            role: 'bot',
                            message: lastMessage.message + (text[index] || ''),
                        },
                    ];
                }
                return prevHistory;
            });

            if (index >= text.length) {
                clearInterval(interval);
                setIsTyping(false);
            }
        }, 50); // Adjust typing speed
    };

    const handleLogout = () => {
        localStorage.removeItem('jwtToken');
        window.location.href = '/signin';
    };

    return (
        <div className="chat-page">
            {/* Chat Header */}
            <div className="chat-header">
                <h2>Language Learning Bot</h2>
                <button onClick={handleLogout} className="logout-button">
                    Logout
                </button>
            </div>

            {/* Chat Body */}
            <div className="chat-body">
                {chatHistory.map((chat, index) => (
                    <div
                        key={index}
                        className={`chat-message ${chat.role === 'user' ? 'user' : 'bot'}`}
                    >
                        <p>{chat.message}</p>
                    </div>
                ))}
                {isTyping && (
                    <div className="chat-message bot">
                        <p>...</p>
                    </div>
                )}
            </div>

            {/* Chat Footer */}
            <div className="chat-footer">
                <textarea
                    placeholder="Type your message..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    className="chat-input"
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault(); // Prevent newline
                            handleAsk();
                        }
                    }}
                />
                <button onClick={handleAsk} className="chat-send-button">
                    Send
                </button>
            </div>
        </div>
    );
};

export default Chat;
