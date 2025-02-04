import React, { useState, useEffect, useRef } from 'react';

function AudioPlayer({ audioSource, type, autoPlayOnMount = false }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [canRender, setCanRender] = useState(true);  // New state for controlling render
  const audioRef = useRef(null);

  useEffect(() => {
    // Create new Audio instance
    audioRef.current = new Audio(
      type === 'snippet' 
        ? `data:audio/mpeg;base64,${audioSource}`
        : audioSource
    );

    // Setup event listeners
    audioRef.current.addEventListener('loadeddata', () => {
      setIsLoaded(true);
      if (autoPlayOnMount && type === 'full') {
        handleAutoPlay();
      }
    });

    audioRef.current.addEventListener('ended', () => {
      setIsPlaying(false);
      // Only remove the player if it's a snippet
      if (type === 'snippet') {
        setCanRender(false);
      }
    });

    // Cleanup
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = '';
      }
    };
  }, [audioSource, type]);

  const handleAutoPlay = async () => {
    try {
      await audioRef.current.play();
      setIsPlaying(true);
    } catch (error) {
      console.log('AutoPlay failed:', error);
      setIsPlaying(false);
    }
  };

  const togglePlay = async () => {
    try {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        await audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (error) {
      console.log('PlayBack failed:', error);
      setIsPlaying(false);
    }
  };

  // Only render if canRender is true
  return (
    <div>
      {isLoaded && canRender && (
        <button
          className={`button ${isPlaying ? 'clicked' : ''}`}
          onClick={togglePlay}
        />
      )}
    </div>
  );
}

export default AudioPlayer;