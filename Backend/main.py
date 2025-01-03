import os
import random
from Spotipy import Spotipy
from flask import Flask, jsonify
from flask_cors import CORS
from flask_cors import cross_origin
from Song import Song
from Game import Game
import requests


app = Flask(__name__)
#CORS(app) #Update when we get an actual domain for the website
game = None

def clear_cache():
    if os.path.exists("../.cache"):
        os.remove("../.cache")

"""
@app.route('/generate-random-song') #Ask what a good naming principle is for
@cross_origin()
def generate_random_song():
    clear_cache()
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    SCOPE = "user-read-playback-state user-top-read user-read-recently-played"

    sp = Spotipy(CLIENT_ID, CLIENT_SECRET, SCOPE)
    sp.authenticate_user()

    tracks = list(set(sp.get_current_user_recently_played(limit=50)))
    #Handle when user doesn't have enough songs (aka len(tracks) ==0) or if persistence is implemented, tracks have already been used
    #Prompt them with something like "Listen to more new music"
    #Test this out by creating a new spotify account and trying the app.
    song_index = random.randint(0, len(tracks) - 1)

    # Randomly chooses one of the 50 most recently played tracks
    chosen_track_id = tracks[song_index]
    song_info = sp.get_track_info(chosen_track_id)
    song = Song(song_info) #TODO: Preserve state of the song and figure out how to transition from this method to the start of the game
    return jsonify(song_info)
"""


@app.route('/start-top-fifty-recents-game')
@cross_origin()
def start_top_fifty_game():
    clear_cache()
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    SCOPE = "user-read-playback-state user-top-read user-read-recently-played"

    sp = Spotipy(CLIENT_ID, CLIENT_SECRET, SCOPE)
    sp.authenticate_user()

    tracks = list(set(sp.get_current_user_recently_played(limit=50)))
    #Handle when user doesn't have enough songs (aka len(tracks) ==0) or if persistence is implemented, tracks have already been used
    #Prompt them with something like "Listen to more new music"
    #Test this out by creating a new spotify account and trying the app.
    song_index = random.randint(0, len(tracks) - 1)
    # Randomly chooses one of the 50 most recently played tracks
    chosen_track_id = tracks[song_index]

    song_info = sp.get_track_info(chosen_track_id)
    song = Song(song_info)
    global game
    game = Game(song)
    return jsonify({"message":"Game started"})

@app.route('/start', methods=['POST'])
def start_game():
    global game
    song_data = request.get_json()
    game = Game(song_data)  # Replace with actual song data structure
    return jsonify({"message": "Game started"})

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

if __name__ == '__main__':
    app.run(debug=True)





