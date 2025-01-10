import React from 'react'


function Artist({song_artist})
{
    return (
        <div >
        <label className="hint">{"Artist: "+ song_artist}</label>
        </div>
    );
}

export default Artist