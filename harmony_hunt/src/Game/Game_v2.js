import React, {useRef, useState} from 'react';
import '../Login/harmony-hunt-logo_480.png';



function Game() {
    const location = useLocation();
    const albumURL = location.state?.gameData;

    async function handleGuess() {
        
      }

    return (
  
        <div className="container">
          <AlbumImage image_url = {albumURL.album_cover} isBlurred = {isBlurred} />
          <div id="guess-box">
            <GuessInput guessRef = {guessRef} handleGuess = {handleGuess} isDisabled = {isDisabled}/>
          </div>
        </div>
        
        
      );
  
}
export default Game;