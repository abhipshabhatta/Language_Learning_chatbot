import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

const SignIn = () => {
    const [email, setEmail] = useState(''); // 'email' represents the input for username
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSignIn = async () => {
      try {
          console.log("Sending signin data:", { username: email, password });
          const response = await axios.post('http://127.0.0.1:5000/auth/signin', {
              username: email, // Ensure 'username' matches backend logic
              password,
          });
  
          if (response.status === 200) {
              localStorage.setItem('jwtToken', response.data.token);
              navigate('/chat');
          }
      } catch (err) {
          console.error("Signin error:", err.response ? err.response.data : err.message);
          setError(err.response?.data?.message || 'An error occurred during sign in. Please try again.');
      }
  };
  

    const handleSignupRedirect = () => {
        navigate('/'); // Redirect to Signup page
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h1>Sign In</h1>
                <input
                    type="text" // Changed type to 'text' to match username field
                    placeholder="Username"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="auth-input"
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="auth-input"
                />
                <button onClick={handleSignIn} className="auth-button">Sign In</button>
                <p className="auth-footer">
                    Don't have an account?{' '}
                    <span className="auth-link" onClick={handleSignupRedirect}>
                        Sign Up
                    </span>
                </p>
                {error && <p className="auth-error">{error}</p>}
            </div>
        </div>
    );
};

export default SignIn;
