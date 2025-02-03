import React from 'react'


function Artist({song_artist})
{
    return (
        <div className="hint-container">
        <label className="hint">{"Artist: "+ song_artist}</label>
        </div>
    );
}

export default Artist