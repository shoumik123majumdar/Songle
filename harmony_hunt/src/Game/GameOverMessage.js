import React from 'react'

const GameOverMessage = ({message, isWon}) => {
    return (
        <div className="game-over-container">
            <div className={isWon ? 'game-over-won' : 'game-over-lost'}>
                {message.prefix}
                <a
                    href={message.spotifyLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`spotify-link ${isWon ? 'won' : 'lost'}`}
                >
                    {message.songName}
                </a>
            </div>
        </div>
    );
}

export default GameOverMessage;