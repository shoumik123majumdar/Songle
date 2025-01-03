import requests


def get_song_preview(song_name,artist_name):
    # Deezer search API endpoint 
    search_url = f"https://api.deezer.com/search"
    
    # Parameters for the search
    params = {
        "q": f'track:"{song_name}" artist:"{artist_name}"',
        "limit": 5  # Get up to 5 results
    }
    
    try:
        # Make the API request
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        
        # Check if we got any results
        if data['total'] > 0:
            preview_urls = []
            
            for i, track in enumerate(data['data']):
                print(f"\nResult {i+1}:")
                print(f"Title: {track['title']}")
                print(f"Artist: {track['artist']['name']}")
                print(f"Album: {track['album']['title']}")
                print(f"Duration: {track['duration']} seconds")
                print(f"Preview URL: {track['preview']}")
                preview_urls.append({
                    'title': track['title'],
                    'artist': track['artist']['name'],
                    'preview_url': track['preview'],
                    'album': track['album']['title'],
                    'duration': track['duration']
                }) 
            
            return preview_urls
        else:
            print(f"No results found for '{song_name}'")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
       

# Example usage
if __name__ == "__main__":
    song_name = input("Enter a song name to search: ")
    artist_name = input("Enter artist name")
    preview_url = get_song_preview(song_name,artist_name)
    
    # Optional: If you want to actually play the preview, you can add this:
    if preview_url and input("Would you like to play the preview? (y/n): ").lower() == 'y':
        try:
            from playsound import playsound
            print("Playing preview...")
            playsound(preview_url)
        except ImportError:
            print("To play the preview, install playsound: pip install playsound")