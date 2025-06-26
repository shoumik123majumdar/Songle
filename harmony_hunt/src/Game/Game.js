import React, {useRef, useState, useEffect} from 'react';
import {useLocation, useNavigate} from 'react-router-dom';
import '../Login/harmony-hunt-logo_480.png';
import AlbumImage from './Hints/AlbumImage'
import GuessInput from './GuessInput';
import Genre from './Hints/Genre'
import ReleaseDate from './Hints/ReleaseDate';
import Artist from './Hints/Artist';
import AudioPlayer from './Hints/AudioPlayer';
import GameOverMessage from './GameOverMessage';
import './game_styles.css'
import axios from 'axios';

// Key for localStorage
const GAME_ID_STORAGE_KEY = 'harmony_hunt_game_id';

function Game() {
    const location = useLocation();
    const navigate = useNavigate();
    
    // Game identification
    const [gameId, setGameId] = useState(() => {
        // Initialize from location state or localStorage
        return location.state?.gameId || localStorage.getItem(GAME_ID_STORAGE_KEY) || null;
    });
    
    // Game state
    const [albumURL, setAlbumURL] = useState(location.state?.albumURL || null);
    const [isBlurred, setIsBlurred] = useState(true);
    const [isDisabled, setIsDisabled] = useState(false);
    const [genre, setGenre] = useState(null);
    const [releaseDate, setReleaseDate] = useState(null);
    const [artist, setArtist] = useState(null);
    const [audioSnippet, setAudioSnippet] = useState(null);
    const [audioClip, setAudioClip] = useState(null);
    const [gameOverMessage, setGameOverMessage] = useState(null);
    const [guesses, setGuesses] = useState([]);
    const [gameOver, setGameOver] = useState(false);
    const [spotifyLink, setSpotifyLink] = useState(null);
    const [gameIsWon, setGameIsWon] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showRecoveredMessage, setShowRecoveredMessage] = useState(null);
    
    const guessRef = useRef(null);

    // Load game state on component mount or when gameId changes
    useEffect(() => {
        const loadGameState = async () => {
            if (gameId) {
                try {
                    setIsLoading(true);
                    setError(null);
                    
                    localStorage.setItem(GAME_ID_STORAGE_KEY, gameId);
                
                    const response = await axios.get(`http://127.0.0.1:5000/get-game-state?game_id=${gameId}`);
                    const data = response.data;
                    
                    updateGameStateFromResponse(data);
                    
                    // Show recovered message if this game was already completed or has special flags
                    if (data.is_existing_game && !location.state?.albumURL) {
                        if (data.game_data_expired) {
                            setShowRecoveredMessage("⚠️ Loaded your game from today (some data may be missing due to cache expiration)");
                        } else if (data.game_data_missing) {
                            setShowRecoveredMessage("⚠️ You've already played today (detailed game data not available)");
                        } else {
                            setShowRecoveredMessage("📱 Loaded your completed game from today!");
                        }
                        setTimeout(() => setShowRecoveredMessage(null), 7000); // Hide after 7 seconds
                    }
                    
                } catch (error) {
                    console.error('Error loading game state:', error);
                    
                    // Handle different error types
                    if (error.response) {
                        const status = error.response.status;
                        const data = error.response.data;
                        
                        if (status === 404) {
                            // Game not found or expired
                            localStorage.removeItem(GAME_ID_STORAGE_KEY);
                            setError('Game not found or expired. Redirecting to start...');
                            setTimeout(() => navigate('/'), 2000);
                        } else if (status === 401 && data.needs_spotify_auth) {
                            // Spotify authentication required
                            localStorage.removeItem(GAME_ID_STORAGE_KEY);
                            setError('Spotify authentication expired. Redirecting to login...');
                            setTimeout(() => navigate('/'), 2000);
                        } else {
                            setError('Failed to load game. Please try again.');
                        }
                    } else {
                        setError('Network error. Please check your connection.');
                    }
                } finally {
                    setIsLoading(false);
                }
            } else if (!location.state?.albumURL) {
                // No gameId and no album URL - redirect to start
                console.log('No game found, redirecting to start...');
                navigate('/');
            } else {
                // This shouldn't happen with the updated LoginButton, but just in case
                setIsLoading(false);
                setError('Game ID missing. Please start a new game.');
                setTimeout(() => navigate('/'), 2000);
            }
        };
        
        loadGameState();
    }, [gameId, albumURL, navigate, location.state]);

    // Helper function to update all game state from server response
    const updateGameStateFromResponse = (data) => {
        console.log('Updating game state with data:', data);
        
        // Use React's unstable_batchedUpdates to ensure all state updates happen together
        // or use a setTimeout to ensure state updates are processed properly
        setTimeout(() => {
            // Set basic game info
            setAlbumURL(data.album_cover);
            
            // Set hints based on what's available - force re-render by ensuring values are set
            setGenre(data.hints?.genre || null);
            setReleaseDate(data.hints?.release_date || null);
            setArtist(data.hints?.artist || null);
            setAudioSnippet(data.hints?.audio_snippet || null);
            setIsBlurred(data.hints?.album_cover_status !== "unblur");
            setAudioClip(data.hints?.full_audio_clip || null);
            setSpotifyLink(data.hints?.spotify_link || null);
            
            // Set previous guesses - ensure we always set an array
            setGuesses(data.previousGuesses || []);
            
            // Check if game is already over and set all related state
            if (data.gameState?.isGameOver) {
                setIsDisabled(true);
                setGameOver(true);
                setGameIsWon(data.gameState.wonGame || false);
                
                if (data.gameState.wonGame) {
                    setGameOverMessage({
                        prefix: `Congratulations! You guessed `,
                        songName: data.gameState.correctSong,
                        spotifyLink: data.hints?.spotify_link
                    });
                } else {
                    setGameOverMessage({
                        prefix: `The correct song was: `,
                        songName: data.gameState.correctSong,
                        spotifyLink: data.hints?.spotify_link
                    });
                }
            } else {
                // Ensure game over state is properly reset for active games
                setIsDisabled(false);
                setGameOver(false);
                setGameIsWon(null);
                setGameOverMessage(null);
            }
            
            console.log('State updates completed');
        }, 0);
    };

    // Handle guess submission
    const handleGuess = async () => {
        if (!guessRef.current.value || !gameId) return;
        
        try {
            const userGuess = guessRef.current.value;
            console.log('Sending guess:', userGuess);
            
            // Include gameId in request
            const response = await axios.post('http://127.0.0.1:5000/make-guess', {
                guess: userGuess,
                game_id: gameId
            });
            
            const data = response.data;
            console.log('Received response:', data);
            
            // Update hints based on response
            if (data.hints.genre) setGenre(data.hints.genre);
            if (data.hints.release_date) setReleaseDate(data.hints.release_date);
            if (data.hints.artist) setArtist(data.hints.artist);
            if (data.hints.audio_snippet) setAudioSnippet(data.hints.audio_snippet);
            if (data.hints.album_cover_status === "unblur") setIsBlurred(false);
            
            // Add the guess to the list
            setGuesses(prev => [...prev, userGuess]);
            
            // Handle game over state
            if (data.gameState.isGameOver) {
                setIsDisabled(true);
                setAudioClip(data.hints.full_audio_clip);
                setGameOver(true);
                setSpotifyLink(data.hints.spotify_link);
                
                if (data.gameState.wonGame) {
                    setGameIsWon(true);
                    setGameOverMessage({
                        prefix: `Congratulations! You guessed `,
                        songName: data.gameState.correctSong,
                        spotifyLink: data.hints.spotify_link
                    });
                } else {
                    setGameIsWon(false);
                    setGameOverMessage({
                        prefix: `The correct song was: `,
                        songName: data.gameState.correctSong,
                        spotifyLink: data.hints.spotify_link
                    });
                }
            }
            
            guessRef.current.value = '';
        } catch (error) {
            console.error('Error submitting guess:', error);
            
            if (error.response) {
                const status = error.response.status;
                const data = error.response.data;
                
                if (status === 404) {
                    // Game expired during play
                    localStorage.removeItem(GAME_ID_STORAGE_KEY);
                    setError('Game expired. Redirecting to start...');
                    setTimeout(() => navigate('/'), 2000);
                } else if (status === 401 && data.needs_spotify_auth) {
                    // Spotify session expired during game
                    localStorage.removeItem(GAME_ID_STORAGE_KEY);
                    setError('Spotify session expired. Redirecting to login...');
                    setTimeout(() => navigate('/'), 2000);
                } else {
                    setError('Failed to submit guess. Please try again.');
                    // Don't redirect, let user try again
                    setTimeout(() => setError(null), 3000);
                }
            } else {
                setError('Network error. Please check your connection.');
                setTimeout(() => setError(null), 3000);
            }
        }
    };

    // Start a new game
    const startNewGame = () => {
        localStorage.removeItem(GAME_ID_STORAGE_KEY);
        navigate('/');
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="loading" style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                fontSize: '18px'
            }}>
                Loading game...
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="error" style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                fontSize: '18px',
                gap: '20px'
            }}>
                <div>{error}</div>
                <button onClick={startNewGame} className="start-button">
                    Start New Game
                </button>
            </div>
        );
    }

    return (
        <div className="game-container">
            {/* Recovered game message */}
            {showRecoveredMessage && (
                <div style={{
                    position: 'fixed',
                    top: '20px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    backgroundColor: showRecoveredMessage.startsWith('⚠️') ? '#f39c12' : '#1db954',
                    color: 'white',
                    padding: '10px 20px',
                    borderRadius: '8px',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
                    zIndex: 1000,
                    fontSize: '14px',
                    maxWidth: '80%',
                    textAlign: 'center'
                }}>
                    {showRecoveredMessage}
                </div>
            )}
            
            <div className="guesses-section">
                <ul className="guess-list">
                    {guesses.map((guess, index) => {
                        const isLastGuess = index === guesses.length - 1;
                        const shouldBeGreen = isLastGuess && gameIsWon;
                        return (
                            <li 
                                key={index} 
                                className={`guess-item ${shouldBeGreen ? 'correct' : 'wrong'}`}
                            >
                                {index + 1}. {guess}
                            </li>
                        );
                    })}
                </ul>
            </div>

            {/* Middle Column - Album and Input */}
            <div className="middle-section">
                <AlbumImage image_url={albumURL} isBlurred={isBlurred} />
                <div id="guess-box">
                    <GuessInput
                        guessRef={guessRef}
                        handleGuess={handleGuess}
                        isDisabled={isDisabled}
                    />
                </div>
                
                <div className="audio-player-container">
                    {/* During game - snippet player */}
                    {audioSnippet && !gameOver && (
                        <AudioPlayer 
                            audioSource={audioSnippet}
                            type="snippet"
                            autoPlayOnMount={false}
                        />
                    )}
                    
                    {/* After game over - full song player */}
                    {gameOver && audioClip && (
                        <AudioPlayer 
                            audioSource={audioClip}
                            type="full"
                            autoPlayOnMount={true}
                        />
                    )}
                </div>

                {gameOverMessage && (
                    <GameOverMessage 
                        message={gameOverMessage}
                        isWon={gameIsWon}
                    />
                )}
                
                {/* Add a "New Game" button when game is over */}
                {gameOver && (
                    <button 
                        className="new-game-button" 
                        onClick={startNewGame}
                        style={{
                            marginTop: '20px',
                            padding: '10px 20px',
                            fontSize: '16px',
                            backgroundColor: '#1db954',
                            color: 'white',
                            border: 'none',
                            borderRadius: '25px',
                            cursor: 'pointer'
                        }}
                    >
                        Play Again Tomorrow
                    </button>
                )}
            </div>

            {/* Right Column - Hints */}
            <div className="hints-section">
                {genre && <Genre song_genre={genre} />}
                {releaseDate && <ReleaseDate song_date={releaseDate} />}
                {artist && <Artist song_artist={artist} />}
            </div>
        </div>
    );
}

export default Game;