import React from 'react'

function Genre({song_genre}) {
    var genre_text = "Genres : "
    for (let i=0; i<song_genre.length-1; i++) {
        genre_text += song_genre[i] + ", "
    }
    genre_text += song_genre[song_genre.length-1]

    return (
        <div className="hint-container">
            <label className="hint genre-hint">{genre_text}</label>
        </div>
    );
}

export default Genre