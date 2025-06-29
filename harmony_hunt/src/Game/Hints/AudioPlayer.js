import React, { useState, useEffect, useRef } from 'react';

function AudioPlayer({ 
    audioSource, 
    type, 
    autoPlayOnMount = false, 
    hasBeenPlayed = false,  // From Game component (only matters for snippets)
    onPlayed = null         // Callback to notify Game component
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const audioRef = useRef(null);

  // Determine if we should show the button
  const shouldShowButton = () => {
    // Full audio clip (end of game) - ALWAYS show button and allow multiple plays
    if (type === 'full') {
      return true;
    }
    
    // Snippet audio (during game) - only show if it hasn't been played yet
    // Once played, button disappears permanently for this game
    if (type === 'snippet') {
      return !hasBeenPlayed;
    }
    
    // Default fallback
    return true;
  };

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
      
      // For snippets, notify parent when audio finishes playing
      // This is when the button should disappear
      if (type === 'snippet' && onPlayed && !hasBeenPlayed) {
        onPlayed();
      }
    });

    // Cleanup
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = '';
      }
    };
  }, [audioSource, type, autoPlayOnMount]);

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
        
        // No immediate onPlayed() call here - let the snippet play
        // Button will disappear when audio ends (in 'ended' event listener)
      }
    } catch (error) {
      console.log('PlayBack failed:', error);
      setIsPlaying(false);
    }
  };

  return (
    <div>
      {isLoaded && shouldShowButton() && (
        <button
          className={`button ${isPlaying ? 'clicked' : ''}`}
          onClick={togglePlay}
        />
      )}
    </div>
  );
}

export default AudioPlayer;