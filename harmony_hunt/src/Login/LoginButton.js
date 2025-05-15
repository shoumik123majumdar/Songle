import axios from 'axios';
import connect_with_spotify from './connect-with-spotify.png';
import {useNavigate} from 'react-router-dom';
import {useState} from 'react';

const LoginButton = () => {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false); //To track whether or not the game is loading after button is clicked

    const handleLogin = async () => {
        if (isLoading) return;
        
        setIsLoading(true); 
        
        try {
            const response = await axios.post('http://127.0.0.1:5000/start-top-fifty-recents-game');
            console.log("Game started successfully")
            navigate('/game', { state: { albumURL: response.data.album_cover } });
        } catch (error) {
            console.error("Failed to login:", error.message);
            setIsLoading(false);
        }
    };

    return (
        <button 
            onClick={handleLogin}
            disabled={isLoading}
            style={{ opacity: isLoading ? 0.7 : 1, cursor: isLoading ? 'not-allowed' : 'pointer' }}
        >
            <img 
                src={connect_with_spotify} 
                className="Connect-with-spotify" 
                width="250" 
                height="50" 
                alt="Connect with spotify" 
            />
        </button>
    );
};

export default LoginButton;