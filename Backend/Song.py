import requests
from io import BytesIO
from pydub import AudioSegment
import base64
import random


class Song:

    def __init__(self,track_info):
        self.track_name =  track_info['track_name']
        self.release_date = track_info['release_date']
        self.artist_name = track_info['artist_name']
        self.album_name = track_info['album_name']
        self.album_image_url = track_info['album_image_url']
        self.genre = track_info['genre']
        self.clip = track_info['clip']
        self.snippet = self._shorten_audio_url(self.clip)

    """
    Gets the song name
    Inputs: N/A
    Outputs:
        - self.track_name: song name
    """
    def get_track_name(self):
        return self.track_name

    """
    Gets the release date of the song
    Inputs: N/A
    Outputs:
        - self.release_date: release date of the song
    """
    def get_release_date(self):
        return self.release_date

    """
    Gets the artist's name
    Inputs: N/A
    Outputs:
        - self.artist_name: artist's name
    """
    def get_artist_name(self):
        return self.artist_name

    """
    Gets the album name
    Inputs: N/A
    Outputs:
        - self.album_name: name of the album 
    """
    def album_name(self):
        return self.album_name()

    """
    Gets the URL of the album image
    Inputs: N/A
    Outputs:
        - self.album_image_url: URL of the album image
    """
    def get_album_image(self):
        return self.album_image_url

    """
    Gets the genre of the song
    Inputs: N/A
    Outputs:
        - self.genre: song's genre
    """
    def get_genre(self):
        return self.genre

    """
    Gets the full audio clip of the song
    Inputs: N/A
    Outputs:
        - self.clip: full audio clip of the song
    """
    def get_clip(self):
        return self.clip

    """
    Gets the shortened snippet of the audio
    Inputs: N/A
    Outputs:
        - self.snippet: shortened 1.5 second audio snippet
    """
    def get_snippet(self):
        return self.snippet()

    """
    HELPER FUNCTION
    Shortens the provided audio URL by extracting a random 1.5-second snippet
    Inputs:
        - audio_url: URL of the full audio clip
    Outputs:
        - base64_audio: base64-encoded 1.5-second audio snippet
    """
    def _shorten_audio_url(self, audio_url):
        # Fetch the audio file
        response = requests.get(audio_url)
        audio_data = BytesIO(response.content)

        # Load the audio file
        audio = AudioSegment.from_mp3(audio_data)

        # Get a random start point
        max_start = len(audio) - 1500  # Subtract 1500 milliseconds from total length
        random_start = random.randint(0, max_start)  # Random start point

        # Extract 1.5 seconds from the random start point
        shortened_audio = audio[random_start:random_start + 1500]

        # Export the audio snippet
        audio_data = shortened_audio.export(format='mp3')
        base64_audio = base64.b64encode(audio_data.read()).decode("utf-8")

        return base64_audio
