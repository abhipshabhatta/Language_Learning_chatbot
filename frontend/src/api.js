import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000'; // Backend URL

export const signin = async (username, password) => {
    const response = await axios.post(`${API_BASE_URL}/auth/signin`, {
        username,
        password,
    });
    return response.data;
};

export const askChatbot = async (token, question) => {
    const response = await axios.post(
        `${API_BASE_URL}/chat/ask`,
        { question },
        {
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        }
    );
    return response.data;
};
