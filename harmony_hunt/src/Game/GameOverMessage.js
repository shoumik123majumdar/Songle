import React from 'react'

const GameOverMessage = ({message}) => {
    return (
        <div className="game-over-container">
            <label className='hint'>
                {message.prefix}
                <a 
                    href={message.spotifyLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="spotify-text-link"
                >
                    {message.songName}
                </a>
                {message.suffix}
            </label>
        </div>
    );
}

export default GameOverMessage;