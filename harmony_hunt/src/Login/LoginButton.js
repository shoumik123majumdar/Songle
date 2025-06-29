import axios from 'axios';
import connect_with_spotify from './connect-with-spotify.png';
import {useState, useRef, useEffect} from 'react';

// Key for localStorage
const GAME_ID_STORAGE_KEY = 'harmony_hunt_game_id';

const LoginButton = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [currentStep, setCurrentStep] = useState('idle'); // 'idle', 'authenticating', 'starting_game'
    const requestInProgress = useRef(false);
    const clickBlocked = useRef(false);
    const lastClickTime = useRef(0);

    // Reset click blocking when loading finishes
    useEffect(() => {
        if (!isLoading) {
            clickBlocked.current = false;
        }
    }, [isLoading]);

    const handleLogin = async () => {
        const now = Date.now();
        
        if (now - lastClickTime.current < 1000) {
            console.log('Click blocked: too soon after last click');
            return;
        }
        
        if (isLoading || requestInProgress.current || clickBlocked.current) {
            console.log('Click blocked: request already in progress');
            return;
        }

        // Layer 3: Immediately set all blocking flags
        lastClickTime.current = now;
        clickBlocked.current = true;
        requestInProgress.current = true;
        setIsLoading(true);

        try {
            setCurrentStep('authenticating');
            console.log('Getting Spotify auth URL...');
            
            const authUrlResponse = await axios.get('http://127.0.0.1:5000/get-auth-url');
            const { auth_url, session_id } = authUrlResponse.data;

            // Store session_id in localStorage for the callback to use
            localStorage.setItem('spotify_session_id', session_id); 

            // Redirect to Spotify OAuth page
            window.location.href = auth_url;

        } catch (error) {
            console.error("Failed to start authentication:", error);
            
            if (error.response) {
                console.log("Error response:", error.response.data);
                alert(error.response.data.error || "Failed to start authentication. Please try again.");
            } else {
                console.log("Network or other error");
                alert("Network error. Please check your connection and try again.");
            }
            
            // Reset ALL loading state on error
            setIsLoading(false);
            requestInProgress.current = false;
            clickBlocked.current = false;
            setCurrentStep('idle');
        }
    };

    const getButtonText = () => {
        switch (currentStep) {
            case 'authenticating':
                return "Connecting to Spotify...";
            case 'starting_game':
                return "Loading your game...";
            default:
                return isLoading ? "Loading..." : "Connect with spotify";
        }
    };

    // Additional protection against double clicks at the button level
    const handleButtonClick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // Final check before calling handleLogin
        if (isLoading || requestInProgress.current || clickBlocked.current) {
            console.log('Button click blocked');
            return;
        }
        handleLogin();
    };

    return (
        <div style={{ textAlign: 'center' }}>
            <button
                onClick={handleButtonClick}
                disabled={isLoading || requestInProgress.current || clickBlocked.current}
                style={{
                    opacity: (isLoading || clickBlocked.current) ? 0.7 : 1,
                    cursor: (isLoading || clickBlocked.current) ? 'not-allowed' : 'pointer',
                    border: 'none',
                    background: 'transparent',
                    pointerEvents: (isLoading || clickBlocked.current) ? 'none' : 'auto'
                }}
            >
                <img
                    src={connect_with_spotify}
                    className="Connect-with-spotify"
                    width="250"
                    height="50"
                    alt={getButtonText()}
                    draggable={false}
                    style={{ 
                        userSelect: 'none',
                        pointerEvents: 'none' // Prevent clicking image directly
                    }}
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