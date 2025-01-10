import requests

class Deezer:

    def find_track_preview_url(self, song_name, artist_name = ""):
        """
        Searches for a track's preview URL using the Deezer API.

        Args:
            song_name (str): Name of the song to search for
            artist_name (str): Name of the artist

        Returns:
            str: Preview URL of the track if found, None otherwise
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
        