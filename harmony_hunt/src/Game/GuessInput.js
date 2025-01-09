import React from 'react';
import './GuessInput.css'

function GuessInput({ handleGuess, guessRef}) {
  const [inputError, setInputError] = useState('');
  const MAX_LENGTH = 50;

  const handleKeyDown = (event) => {
      // Clear error when user starts typing
      setInputError('');

      if (event.key === 'Enter') {
          const guess = guessRef.current.value.trim();
          
          // Input validation
          if (guess.length === 0) {
              setInputError('Please enter a guess');
              return;
          }
          if (guess.length > MAX_LENGTH) {
              setInputError(`Guess must be ${MAX_LENGTH} characters or less`);
              return;
          }

          handleGuess();
      }
  };

  const handleInput = (event) => {
      if (event.target.value.length > MAX_LENGTH) {
          setInputError(`Maximum ${MAX_LENGTH} characters allowed`);
      } else {
          setInputError('');
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
              placeholder="Enter Guess..."
              disabled={isDisabled}
              maxLength={MAX_LENGTH}
          />
          {inputError && <div className="input-error">{inputError}</div>}
      </div>
  );
}