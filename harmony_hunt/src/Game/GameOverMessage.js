import React from 'react'

const GameOverMessage = ({message}) => {
    return (
        <div>
            <label className='hint'>{message}</label>
        </div>
    );
}

export default GameOverMessage;