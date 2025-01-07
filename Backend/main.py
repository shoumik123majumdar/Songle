import os
import random
from Spotipy import Spotipy
from Deezer import Deezer
from flask import Flask, jsonify
from flask_cors import CORS
from flask_cors import cross_origin
from Song import Song
from Game import Game
import requests


app = Flask(__name__)
CORS(app) #Update when we get an actual domain for the website
game = None

def clear_cache():
    if os.path.exists("../.cache"):
        os.remove("../.cache")


@app.route('/start-top-fifty-recents-game')
@cross_origin()
def start_top_fifty_game():
    clear_cache()
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    SCOPE = "user-read-playback-state user-top-read user-read-recently-played"
    
    sp = Spotipy(CLIENT_ID, CLIENT_SECRET, SCOPE)
    sp.authenticate_user()
    deezer = Deezer()
    recently_played_track_id_list = list(set(sp.get_current_user_recently_played(limit=50)))
    song = None

    while(True):
        if len(recently_played_track_id_list)==0:
            return jsonify({"error":"Not enough recent tracks (or no song data could be found for them). Listen to more music and come back!"}) #Test this functionality out with a new Spotify account
    
        song_index = random.randint(0, len(recently_played_track_id_list) - 1)  
        chosen_track_id = recently_played_track_id_list[song_index] # Randomly chooses one of the 50 most recently played tracks
        track_info = sp.get_track_info(chosen_track_id) # Get track information from Spotify
        preview_url= deezer.find_track_preview_url(track_info["track_name"],track_info["artist"]) # Attempts to find track from deezer
        
        if preview_url: # if 30 second preview url exists for the track, choose the song to start the game...
            track_info['clip'] = preview_url
            song = Song(track_info)
            break
        else: # if not, continue looping through the recently_played_track_id_list 
            recently_played_track_id_list.pop(song_index)

    global game
    game = Game(song)
    #Return the album cover to be rendered on the user-side
    return jsonify({"album_cover":f"{song.get_album_image()}"})


"""

@app.route('/make-guess', methods=['POST'])
def make_guess():
    if not game:
        return jsonify({"error": "Game not started"}), 400

    guess = request.get_json().get("guess")
    hint = game.process_guess(guess)

    if hint == "unblur":
        return jsonify({"action": "unblur"})
    else:
        return jsonify({"hint": hint})


@app.route('/end-game', methods=['POST'])
def end_game():
    if not game:
        return jsonify({"error": "Game not started"}), 400

    game._end_game()
    return jsonify({"message": "Game ended"})
"""

if __name__ == '__main__':
    app.run(debug=True)





