import React from 'react'

function ReleaseDate({song_date})
{
    const finalDate = song_date.substring(5) + "-" + song_date.substring(0,4);
    const genre_text = "Release Date : " + finalDate

    return (
        <div >
        <label className="hint">{genre_text}</label>
        </div>
    );
}

export default ReleaseDate