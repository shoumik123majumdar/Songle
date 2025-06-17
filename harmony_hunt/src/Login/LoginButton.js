import axios from 'axios';
import connect_with_spotify from './connect-with-spotify.png';
import {useNavigate} from 'react-router-dom';
import {useState, useRef} from 'react';

// Key for localStorage
const GAME_ID_STORAGE_KEY = 'harmony_hunt_game_id';

const LoginButton = () => {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const requestInProgress = useRef(false); // Prevent double requests

    const handleLogin = async () => {
        // Prevent double clicks and multiple requests
        if (isLoading || requestInProgress.current) {
            console.log('Request already in progress, ignoring click');
            return;
        }

        setIsLoading(true);
        requestInProgress.current = true;

        try {
            console.log('Starting new game...');
            const response = await axios.post('http://127.0.0.1:5000/start-top-fifty-recents-game');
            console.log("Game started successfully:", response.data);

            // Extract data from standardized response
            const { game_id, album_cover } = response.data;

            // Store game ID in localStorage
            localStorage.setItem(GAME_ID_STORAGE_KEY, game_id);

            // Navigate to game with both game_id and album_cover
            navigate('/game', {
                state: {
                    gameId: game_id,
                    albumURL: album_cover
                },
                replace:true
            });
        } catch (error) {
            console.error("Failed to start game:", error.message);
            // Reset loading state on error so user can try again
            setIsLoading(false);
            requestInProgress.current = false;
            // You might want to show an error message to the user here
        }
        // Note: We don't reset loading/requestInProgress on success because 
        // we're navigating away from this component
    };

    return (
        <button
            onClick={handleLogin}
            disabled={isLoading}
            style={{
                opacity: isLoading ? 0.7 : 1,
                cursor: isLoading ? 'not-allowed' : 'pointer',
                border: 'none',
                background: 'transparent',
                // Add pointer-events to prevent any clicking during loading
                pointerEvents: isLoading ? 'none' : 'auto'
            }}
        >
            <img
                src={connect_with_spotify}
                className="Connect-with-spotify"
                width="250"
                height="50"
                alt={isLoading ? "Starting game..." : "Connect with spotify"}
                // Prevent drag/selection that might interfere with clicking
                draggable={false}
                style={{ userSelect: 'none' }}
            />
        </button>
    );
};

export default LoginButton;