import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from io import BytesIO
from pydub import AudioSegment
import pandas
import base64
import random


class Spotipy:
    """
    A wrapper class for interacting with the Spotify Web API.

    Attributes:
        CLIENT_ID (str): The Spotify API client ID
        CLIENT_SECRET (str): The Spotify API client secret
        CLIENT_SCOPE (str): The requested scope of permissions
        sp (spotipy.Spotify): The authenticated Spotify client instance  
        USER_ID (str): The authenticated user's Spotify ID
    """

    def __init__(self, CLIENT_ID, CLIENT_SECRET,SCOPE):
        """
        Initialize the Spotipy wrapper with client credentials.

        Args:
            CLIENT_ID (str): Spotify API client ID
            CLIENT_SECRET (str): Spotify API client secret  
            SCOPE (str): Requested API permission scopes
        """
        self.CLIENT_ID = CLIENT_ID
        self.CLIENT_SECRET = CLIENT_SECRET
        self.CLIENT_SCOPE = SCOPE
        self.sp = None
        self.USER_ID = None

    def authenticate_user(self):
        """
        Authenticate with Spotify using OAuth flow.
        Sets up the authenticated Spotify client and gets user ID.
        """
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id= self.CLIENT_ID,
            client_secret= self.CLIENT_SECRET,
            redirect_uri="http://localhost:3000/callback",
            scope=  self.CLIENT_SCOPE,
            show_dialog=True
        ))
        self.USER_ID = self.sp.current_user()['id']

    #  Helper Method
    def __get_artists(self, list):
        """
        Format a list of artist names into a readable string.

        Args:
            list (List[str]): List of artist names

        Returns:
            str: Formatted string of artist names (e.g. "Artist1, Artist2, and Artist3")
        """
        returnable = ""
        if (len(list) == 1):
            return str(list[0])
        elif (len(list) == 2):
            return str(list[0]) + " and " + str(list[1])
        else:
            for i in range(len(list) - 1):
                returnable += str(list[i]) + ", "
            returnable += "and " + str(list[len(list) - 1])
            return returnable

    def get_current_track(self, printable=False):
        """
        Get information about the currently playing track.

        Args:
            printable (bool): Whether to print track info to console

        Returns:
            str: Track ID if a track is playing
            bool: False if nothing is playing
        """
        response = self.sp.current_playback()
        if response != None:
            device_name = response['device']['name']
            song_name = response['item']['name']
            artists = self.__get_artists([artist['name'] for artist in response['item']['artists']])
            album_name = response['item']['album']['name']
            if printable: print(
                f'The song currently playing from your {device_name} is {song_name} by {artists} from the album: {album_name}')
            return response['item']['id']
        else:
            if printable: print(
                "Nothing is currently playing"
            )
            return False

    def get_current_user_playlists(self):
        """
        Get list of current user's playlists.

        Returns:
            List[str]: List of playlist names
            bool: False if no playlists found
        """
        response = self.sp.current_user_playlists()
        list_playlists = []
        if response != None:
            for item in response['items']:
                list_playlists.append(item['name'])
            return list_playlists
        else:
            return False

    def create_playlist(self, name, description=""):
        """
        Create a new playlist for the current user.

        Args:
            name (str): Name of the playlist
            description (str, optional): Description of the playlist. Defaults to empty string.
        """
        self.sp.user_playlist_create(self.USER_ID, public=True, description=description, name=name)

    def get_playlist_id(self, playlist_name):
        """
        Get the Spotify ID for a playlist by name.

        Args:
            playlist_name (str): Name of the playlist

        Returns:
            str: Playlist ID if found
        """
        list = self.sp.user_playlists(self.USER_ID)['items']
        for item in list:
            if item['name'] == playlist_name:
                return item['id']

    def add_to_playlist(self, playlist_name, song_id=None):
        """
        Add tracks to a specified playlist.

        Args:
            playlist_name (str): Name of the target playlist
            song_id (str/List[str], optional): Track ID(s) to add. If None, adds currently playing track.
        """
        playlist_id = self.get_playlist_id(playlist_name)
        if song_id is None:
            song_id = [self.get_current_track()]
        self.sp.playlist_add_items(playlist_id, song_id)

    
    def __get_top(self,item_type,limit):
        """
        Helper method to get user's top tracks or artists.

        Args:
            item_type (str): Type of items to get ("track" or "artist")
            limit (int): Number of items to retrieve

        Returns:
            List[str]: List of track/artist names
        """
        list_item = []
        if(item_type == "track"):
            track_response = self.sp.current_user_top_tracks(limit=limit)
            list_item = [track['name'] for track in track_response['items']]
        elif(item_type == "artist"):
            artist_response = self.sp.current_user_top_artists(limit=limit)
            list_item = [artist['name'] for artist in artist_response['items']]
        print(pandas.DataFrame(zip(list_item), columns=[f"Top {len(list_item)} {item_type.capitalize()}s"]))
        return list_item

    def get_current_user_top_songs(self, track_limit=5):
        """
        Get current user's top tracks.

        Args:
            track_limit (int, optional): Number of tracks to retrieve. Defaults to 5.

        Returns:
            List[str]: List of top track names if a track is currently playing
        """
        if self.get_current_track():
            return self.__get_top("track",track_limit)
        else:
            print("Nothing is currently playing")

    def get_current_user_top_artists(self,artist_limit=5):
        """
        Get current user's top artists.

        Args:
            artist_limit (int, optional): Number of artists to retrieve. Defaults to 5.

        Returns:
            List[str]: List of top artist names
        """
        return self.__get_top("artist",artist_limit)

    
    def get_current_user_recently_played(self,limit=50):
        """
        Get user's recently played tracks.

        Args:
            limit (int, optional): Number of tracks to retrieve. Defaults to 50.

        Returns:
            List[str]: List of track IDs
        """
        response = self.sp.current_user_recently_played(limit=limit)['items']
        tracks = []
        for item in response:
            tracks.append( item['track']['id'])
        return tracks

   
    def get_track_info(self,track_id):
        """
        Get detailed information about a specific track.

        Args:
            track_id (str): Spotify track ID

        Returns:
            dict: Dictionary containing track information including:
                - track_name: Name of the track
                - release_date: Release date of the album
                - artist_name: Name of the primary artist
                - album_name: Name of the album
                - album_image_url: URL of album cover image
                - genre: List of artist genres
                - clip: Preview URL for the track
                - snippet: Base64 encoded short audio snippet
        """
        track = self.sp.track(track_id = track_id)
        track_info = {}

        track_info['track_name'] = self.clean_track_name(track["name"])
        track_info['release_date'] = track['album']['release_date']
        track_info['artist_name'] = track['artists'][0].get('name')
        track_info['album_name'] = track['album']['name']
        track_info['album_image_url'] = track['album']['images'][0]['url']

        artist_id = track['artists'][0]['id']
        artist_info = self.sp.artist(artist_id)
        track_info['genre'] = artist_info['genres']

        track_info['clip'] = track['preview_url']
        track_info['snippet'] = self.shorten_audio_url(track['preview_url'])

        return track_info


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

    def clean_track_name(self,track_name):
        """
        Remove extra information from track names (e.g. "(feat. Artist)" or "- Remix").

        Args:
            track_name (str): Original track name

        Returns:
            str: Cleaned track name
        """
        for i,char in enumerate(track_name):
            if char in ["(", "-"]:
                return track_name[:i].strip()
        return track_name

