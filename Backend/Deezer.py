import requests

class Deezer:
        
    def __init__(self, ):
        self.access_token = access_token

    def find_track_preview_url(self, song_name,artist_name):
        
    def shorten_audio_url(self, audio_url):
        """
        Create a shortened audio snippet from a track's preview URL.

        Args:
            audio_url (str): URL of the track preview audio

        Returns:
            str: Base64 encoded 1.5 second audio snippet
        """
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