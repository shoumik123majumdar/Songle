import React, { useState } from 'react';

function AudioPlayer({ base64Audio}) {
  const [canPlay, setCanPlay] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);

  function handlePlayClick() {
    if (canPlay) {
      setIsPlaying(true); // Change state to indicate playing
      const audio = new Audio(`data:audio/mpeg;base64,${base64Audio}`);
      audio.play();
      audio.onended = () => {
        // Once playback ends, change state back
        setIsPlaying(false);
        setCanPlay(false);
      };
    }
  }

  return (
    <div>
      {canPlay && (
        <button
          className={`button ${isPlaying ? 'clicked' : ''}`}
          onClick={handlePlayClick}
        >
        </button>
      )}
    </div>
  );
}

export default AudioPlayer;