import axios from 'axios';
import connect_with_spotify from './connect-with-spotify.png';
import {useNavigate} from 'react-router-dom';
import {useState, useRef} from 'react';

// Key for localStorage
const GAME_ID_STORAGE_KEY = 'harmony_hunt_game_id';

const LoginButton = () => {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const [currentStep, setCurrentStep] = useState('idle'); // 'idle', 'authenticating', 'starting_game'
    const requestInProgress = useRef(false);

    const handleLogin = async () => {
        // Prevent double clicks and multiple requests
        if (isLoading || requestInProgress.current) {
            console.log('Request already in progress, ignoring click');
            return;
        }

        setIsLoading(true);
        requestInProgress.current = true;

        try {
            // Step 1: Authenticate with Spotify
            setCurrentStep('authenticating');
            console.log('Authenticating with Spotify...');
            
            const authResponse = await axios.post('http://127.0.0.1:5000/spotify-login');
            console.log("Spotify authentication successful:", authResponse.data);

            // Step 2: Start the game
            setCurrentStep('starting_game');
            console.log('Starting new game...');
            
            const gameResponse = await axios.post('http://127.0.0.1:5000/start-top-fifty-recents-game');
            console.log("Game started successfully:", gameResponse.data);

            // Extract data from response
            const { game_id, album_cover } = gameResponse.data;

            // Store game ID in localStorage
            localStorage.setItem(GAME_ID_STORAGE_KEY, game_id);

            // Navigate to game
            navigate('/game', {
                state: {
                    gameId: game_id,
                    albumURL: album_cover
                },
                replace: true
            });

        } catch (error) {
            console.error("Failed to start game:", error);
            
            // Handle different types of errors
            if (error.response) {
                const status = error.response.status;
                const data = error.response.data;
                
                if (status === 401 && data.needs_spotify_auth) {
                    console.log("Spotify authentication required");
                    alert("Spotify authentication failed. Please try again.");
                } else if (status === 429) {
                    console.log("User already played today");
                    alert(data.error || "You've already played today! Come back tomorrow.");
                } else if (status === 400) {
                    console.log("Not enough recent tracks");
                    alert(data.error || "Not enough recent tracks found. Listen to more music and try again!");
                } else {
                    console.log("Other error:", data.error);
                    alert(data.error || "Failed to start game. Please try again.");
                }
            } else {
                console.log("Network or other error");
                alert("Network error. Please check your connection and try again.");
            }
            
            // Reset loading state on error
            setIsLoading(false);
            requestInProgress.current = false;
            setCurrentStep('idle');
        }
    };

    const getButtonText = () => {
        switch (currentStep) {
            case 'authenticating':
                return "Connecting to Spotify...";
            case 'starting_game':
                return "Starting game...";
            default:
                return isLoading ? "Loading..." : "Connect with spotify";
        }
    };

    return (
        <div style={{ textAlign: 'center' }}>
            <button
                onClick={handleLogin}
                disabled={isLoading}
                style={{
                    opacity: isLoading ? 0.7 : 1,
                    cursor: isLoading ? 'not-allowed' : 'pointer',
                    border: 'none',
                    background: 'transparent',
                    pointerEvents: isLoading ? 'none' : 'auto'
                }}
            >
                <img
                    src={connect_with_spotify}
                    className="Connect-with-spotify"
                    width="250"
                    height="50"
                    alt={getButtonText()}
                    draggable={false}
                    style={{ userSelect: 'none' }}
                />
            </button>
            
            {/* Show current step to user */}
            {isLoading && (
                <div style={{ 
                    marginTop: '10px', 
                    fontSize: '14px', 
                    color: '#666' 
                }}>
                    {getButtonText()}
                </div>
            )}
        </div>
    );
};

export default LoginButton;