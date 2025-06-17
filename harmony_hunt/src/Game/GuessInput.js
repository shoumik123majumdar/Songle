import React, { useState, useEffect} from 'react';
import './GuessInput.css'

function GuessInput({ handleGuess, guessRef, isDisabled}) {
  const MAX_LENGTH = 50;
  const [placeholder, setPlaceHolder] = useState('Enter Song Guess...')
  // This effect runs whenever isDisabled changes
  useEffect(() => {setPlaceHolder(isDisabled ? 'Game Over' : 'Enter Song Guess...');}, [isDisabled]);

  const handleKeyDown = (event) => {
      if (event.key === 'Enter') {
          const guess = guessRef.current.value.trim();
          
          // Input validation
          if (guess.length === 0) {
              setPlaceHolder('Please enter a song guess');
              return;
          }
          if (guess.length > MAX_LENGTH) {
              setPlaceHolder(`Song guess must be ${MAX_LENGTH} characters or less`);
              return;
          }

          handleGuess();
      }
  };

  const handleInput = (event) => {
      if (event.target.value.length > MAX_LENGTH) {
          setPlaceHolder(`Maximum ${MAX_LENGTH} characters allowed`) }
     else {
        event.target.value = event.target.value.slice(0, MAX_LENGTH);
        setPlaceHolder('Enter Song Guess...')
     }     
  };

  return (
      <div className="input-container">
          <input 
              ref={guessRef} 
              onKeyDown={handleKeyDown}
              onInput={handleInput}
              type="text" 
              className="spotify-input"
              placeholder= {placeholder}
              disabled={isDisabled}
              maxLength={MAX_LENGTH}
          />
      </div>
  );
}
export default GuessInput;