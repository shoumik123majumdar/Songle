import os
import random
from Spotipy import Spotipy
from Deezer import Deezer
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_cors import cross_origin
from Song import Song
from Game import Game
from dotenv import load_dotenv
import uuid
import redis
import pickle

#TODO: Make sure you solve how the backend will handle a user refreshing the page. 
load_dotenv()
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Connect to Redis
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    db=int(os.environ.get('REDIS_DB', 0)),
    decode_responses=False  # Keep binary data as-is for pickled objects
)


def clear_cache():
    """
    Clear cookie cache
    """
    if os.path.exists("../.cache"):
        os.remove("../.cache")

def save_game_to_redis(game_id, game_obj):
    """Serialize and save game object to Redis with 24-hour expiration"""
    try:
        serialized_game = pickle.dumps(game_obj)
        redis_client.setex(f"game:{game_id}", 86400, serialized_game)  # 24 hours expiration
        return True
    except Exception as e:
        print(f"Error saving game to Redis: {e}")
        return False
    
def load_game_from_redis(game_id):
    """Load and deserialize game object from Redis"""
    try:
        serialized_game = redis_client.get(f"game:{game_id}")
        if serialized_game:
            return pickle.loads(serialized_game)
        return None
    except Exception as e:
        print(f"Error loading game from Redis: {e}")
        return None

@app.route('/start-top-fifty-recents-game', methods=['POST'])
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
        preview_url= deezer.find_track_preview_url(track_info["track_name"],track_info["artist_name"]) # Attempts to find track from deezer
        
        if preview_url: # if 30 second preview url exists for the track, choose the song to start the game...
            track_info['clip'] = preview_url
            song = Song(track_info)
            break
        else: # if not, continue looping through the recently_played_track_id_list 
            recently_played_track_id_list.pop(song_index)
    
    game = Game(song) #Initialize game object
    game_id = str(uuid.uuid4())
    save_game_to_redis(game_id, game)

    response = game.get_current_state()
    response["game_id"] = game_id
    return jsonify(response)




@app.route('/make-guess', methods=['POST'])
@cross_origin()
def make_guess():
    # Get game ID from request body
    data = request.get_json()
    
    game_id = data['game_id']
    guess = data['guess']
    
    # Load game from Redis
    game = load_game_from_redis(game_id)
    if not game:
        return jsonify({"error": "Game not found or expired"}), 404
    
    response = game.process_guess(guess)

    save_game_to_redis(game_id, game)
    
    return jsonify(response)

@app.route('/get-game-state', methods=['GET'])
@cross_origin()
def get_game_state():
    game_id = request.args.get('game_id')
    if not game_id:
        return jsonify({"error": "No game_id provided"}), 400
    
    game = load_game_from_redis(game_id)
    if not game:
        return jsonify({"error": "Game not found or expired"}), 404
    
    response = game.get_current_state()
    response["game_id"] = game_id  # Add game_id to response
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)