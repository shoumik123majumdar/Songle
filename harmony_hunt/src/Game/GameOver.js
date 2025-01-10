import React from 'react'


function GameOver({gameOverMessage})
{
    return (
        <div >
            <label className='hint'> {gameOverMessage} </label>
        </div>
    );

    }

export default GameOver