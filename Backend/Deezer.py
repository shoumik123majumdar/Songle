import requests

class Deezer:

    def find_track_preview_url(self, song_name, artist_name):
        """
        Searches for a track's preview URL using the Deezer API.

        Args:
            song_name (str): Name of the song to search for
            artist_name (str): Name of the artist

        Returns:
            str: Preview URL of the track if found, None otherwise
            base_64: 1.5 second audio snippet of the track if found, None otherwise
        """
        # Construct the search query with song and artist
        song_query = f"{song_name} {artist_name}"
        search_url = f"https://api.deezer.com/search?q={song_query}"

        # Make request to Deezer API
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            results = response.json()

            # Check if any tracks were found
            if results.get('data') and len(results['data']) > 0:
                # Get the preview URL from the first result
                preview_url = results['data'][0].get('preview')
                return preview_url
            
            return None

        except requests.exceptions.RequestException:
            return None
        
    def shorten_audio_url(self, audio_url):
        """
        Helper method to create a shortened audio snippet from a track's preview URL.

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
    

if __name__ == "__main__":
    deez_nuts = Deezer()
    print(deez_nuts.find_track_preview_url("Money Trees","Kendrick Lamar"))

