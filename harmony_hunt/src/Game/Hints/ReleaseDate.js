import React from 'react'

function ReleaseDate({song_date})
{
    const genre_text = "Release Date : " + song_date
    return (
        <div >
        <label className="hint">{genre_text}</label>
        </div>
    );
}

export default ReleaseDate