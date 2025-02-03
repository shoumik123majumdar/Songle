import React, {useRef, useState} from 'react';
import {useLocation} from 'react-router-dom';
import '../Login/harmony-hunt-logo_480.png';
import AlbumImage from './Hints/AlbumImage'
import GuessInput from './GuessInput';
import Genre from './Hints/Genre'
import ReleaseDate from './Hints/ReleaseDate';
import Artist from './Hints/Artist';
import AudioPlayer from './Hints/AudioPlayer';
import GameOverMessage from './GameOverMessage';
import  './game_styles.css'

function Game() {
    const location = useLocation();
    const albumURL = location.state?.albumURL;
    const [isBlurred, setIsBlurred] = useState(true);
    const [isDisabled, setIsDisabled] = useState(false);
    const [genre,setGenre] = useState(null);
    const [releaseDate,setReleaseDate] = useState(null);
    const [artist,setArtist] = useState(null);
    const [audioSnippet,setAudioSnippet] = useState(null);
    const [audioClip, setAudioClip] = useState(null);
    const [gameOverMessage, setGameOverMessage] = useState(null);
    const [guesses, setGuesses] = useState([]);

    const guessRef = useRef(null)


    async function handleGuess() {
      try {
          const userGuess = guessRef.current.value;
          const response = await fetch('http://localhost:5000/make-guess', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({ guess: userGuess })
          });
          console.log('Sending guess:', userGuess);

          
  
          const data = await response.json();
          console.log('Received response:', data);
          console.log('Hints:', data.hints);
          console.log('Game State:', data.gameState);

          
          if (data.hints.genre) {
              setGenre(data.hints.genre);
          }
          if (data.hints.release_date) {
              setReleaseDate(data.hints.release_date);
          }
          if (data.hints.artist) {
              setArtist(data.hints.artist);
          }
          if (data.hints.audio_snippet) {
              setAudioSnippet(data.hints.audio_snippet);
          }
          if (data.hints.album_cover_status === "unblur") {
              setIsBlurred(false);
          }
  
          setGuesses(prev => [...prev, userGuess])
          if (data.gameState.isGameOver) {
              setIsDisabled(true);
              setAudioClip(data.hints.full_audio_clip)
              if (data.gameState.wonGame) {
                  setGameOverMessage(`Congratulations! You won in ${data.gameState.guessCount} guesses!`);
                  
              } else {
                  setGameOverMessage(`Game Over! The correct song was: ${data.gameState.correctSong}`);
                  //ADD MORE TO THIS COMPONENT, LIKE A LINK TO LISTEN TO THE FULL SONG
              }
          }
  
          guessRef.current.value = '';
      } catch (error) {
          console.error('Error fetching guess from server', error);
      }
  }

    return (
  
        <div className="game-container">
        {/* Left Column - Guesses */}
        <div className="guesses-section">
            <h2>Guesses</h2>
            <ul className="guess-list">
                {guesses.map((guess, index) => (
                    <li key={index} className="guess-item">
                        {index + 1}. {guess}
                    </li>
                ))}
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
            {gameOverMessage && (
                <>
                    <GameOverMessage message={gameOverMessage} className="hint" />
                    {audioClip && <audio src={audioClip} autoPlay></audio>}
                </>
            )}
        </div>

        {/* Right Column - Hints */}
        <div className="hints-section">
            {genre && <Genre song_genre={genre} />}
            {releaseDate && <ReleaseDate song_date={releaseDate} />}
            {artist && <Artist song_artist={artist} />}
            {audioSnippet && <AudioPlayer base64Audio={audioSnippet} />}
        </div>
    </div>  
);
  
}
export default Game;