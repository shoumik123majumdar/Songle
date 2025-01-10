import React from 'react';
import './AlbumImage.css'

function AlbumImage({image_url,isBlurred}) 
{
    return (
        <img src= {image_url} alt = "Album Cover" className = {isBlurred ? 'blurred' : ''} />
    );
}
export default AlbumImage