import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Signup from './components/SignUp';
import SignIn from './components/SignIn';
import Chat from './components/Chat';
import './App.css';

function App() {
    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route path="/" element={<Signup />} />
                    <Route path="/signin" element={<SignIn />} />
                    <Route path="/chat" element={<Chat />} /> {/* Route for Chat */}
                </Routes>
            </div>
        </Router>
    );
}

export default App;
