import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

const SignUp = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSignUp = async () => {
      try {
          console.log("Sending signup data:", { username, password });
          const response = await axios.post('http://127.0.0.1:5000/auth/signup', {
              username,
              password,
          });
          console.log("Signup response:", response.data);
  
          if (response.status === 201) {
              navigate('/signin');
          }
      } catch (err) {
          console.error("Signup error:", err.response ? err.response.data : err.message);
          setError(err.response?.data?.message || 'An error occurred during sign up. Please try again.');
      }
  };
  
  
  
    const handleSignInRedirect = () => {
        navigate('/signin'); // Redirect to Sign In page
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Welcome to LangBot!</h2>
                <button className="social-login facebook">Sign up with Facebook</button>
                <button className="social-login google">Sign up with Google</button>
                <div className="divider">
                    <span>OR</span>
                </div>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="auth-input"
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="auth-input"
                />
                <input
                    type="password"
                    placeholder="Password*"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="auth-input"
                />
                <button onClick={handleSignUp} className="auth-button">Sign Up</button>
                <p className="auth-footer">
                    Already have an account?{' '}
                    <span className="auth-link" onClick={handleSignInRedirect}>
                        Sign In
                    </span>
                </p>
                {error && <p className="auth-error">{error}</p>}
            </div>
        </div>
    );
};

export default SignUp;
