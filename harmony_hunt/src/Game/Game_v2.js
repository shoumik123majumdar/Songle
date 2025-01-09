import React, {useRef, useState, useLocation} from 'react';
import '../Login/harmony-hunt-logo_480.png';



function Game() {
    const location = useLocation();
    const albumURL = location.state?.gameData;
    const [isBlurred, setIsBlurred] = useState(true);
    const [isDisabled, setIsDisabled] = useState(false);

    async function handleGuess() {
      try {
        const userGuess = guessRef.current.value;
        const response = await fetch('/make-guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                guess: userGuess  // Replace with actual guess value
            })
        });

        const data = await response.json();
        
        if (data.action === "unblur") {
          setIsBlurred(false)
        } else if (data.hint) {
            // Handle hint
        }
        //Make sure to disable GuessInput after game is over response from backend
        guessRef.current.value = ''
    } catch (error) {
        console.error('Error fetching guess from server', error);
    }

      }

    return (
  
        <div className="container">
          <AlbumImage image_url = {albumURL.album_cover} isBlurred = {isBlurred} />
          <div id="guess-box">
            <GuessInput 
                guessRef = {guessRef} 
                handleGuess = {handleGuess} 
            />
          </div>
        </div>
        
        
      );
  
}
export default Game;