import os
import time
import uuid
import glob
import pickle
import random
import redis
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from Spotipy import Spotipy
from Deezer import Deezer
from Song import Song
from Game import Game

load_dotenv()

app = Flask(__name__)
CORS(app)

redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    db=int(os.environ.get('REDIS_DB', 0)),
    decode_responses=False
)

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:3000/callback")

# ------------- UTILITIES ------------- #
def clear_cache():
    try:
        for file in glob.glob(".cache*"):
            os.remove(file)
            print(f"Removed cache file: {file}")
    except Exception as e:
        print(f"Error clearing cache: {e}")

def get_cached_spotify_session(user_id):
    try:
        data = redis_client.get(f"spotify_session:{user_id}")
        if data:
            return pickle.loads(data)
    except Exception as e:
        print(f"Error loading cached session: {e}")
    return None

def save_game_to_redis(game_id, game):
    try:
        redis_client.setex(f"game:{game_id}", 86400, pickle.dumps(game))
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        return False

def load_game_from_redis(game_id):
    try:
        data = redis_client.get(f"game:{game_id}")
        if data:
            return pickle.loads(data)
    except Exception as e:
        print(f"Error loading game: {e}")
    return None

def mark_user_played_today(user_id, game_id):
    today_key = f"user_play:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
    redis_client.setex(today_key, 86400, game_id)

def can_user_play_today(user_id):
    today_key = f"user_play:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
    return True #not redis_client.exists(today_key)

def get_user_todays_game(user_id):
    today_key = f"user_play:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
    data = redis_client.get(today_key)
    return data.decode() if data else None

# ------------- AUTH FLOW ------------- #
@app.route('/get-auth-url', methods=['GET'])
@cross_origin()
def get_auth_url():
    session_id = f"session_{int(time.time())}"
    scope = "user-read-playback-state user-top-read user-read-recently-played"
    sp = Spotipy(CLIENT_ID, CLIENT_SECRET, scope, session_id=session_id)
    auth_url = sp.get_auth_url(REDIRECT_URI)
    return jsonify({"auth_url": auth_url, "session_id": session_id})

@app.route('/exchange-code', methods=['POST'])
@cross_origin()
def exchange_code():
    """
    Exchange Spotify authorization code for access tokens and return user info.
    This replaces the redirect-based spotify-callback.
    """
    clear_cache()
    data = request.get_json()
    code = data.get("code")
    state = data.get("state")  # This is the session_id
    
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    try:
        # Create Spotipy instance with the session_id
        sp = Spotipy(CLIENT_ID, CLIENT_SECRET, scope="user-read-playback-state user-top-read user-read-recently-played", session_id=state)
        
        # Complete the OAuth flow
        sp.complete_auth(code, REDIRECT_URI)
        
        # Get user info
        user_info = sp.sp.current_user()
        sp.USER_ID = user_info["id"]
        sp.display_name = user_info.get("display_name", "Unknown")

        # Cache the session in Redis for future API calls
        redis_client.setex(f"spotify_session:{sp.USER_ID}", 3600, pickle.dumps(sp))
        print(f"Authenticated and cached Spotify session for {sp.USER_ID}")

        # Return user info as JSON (no redirect!)
        return jsonify({
            "spotify_user_id": sp.USER_ID,
            "display_name": sp.display_name
        })
        
    except Exception as e:
        print(f"OAuth exchange failed: {e}")
        return jsonify({"error": "Authentication failed"}), 401

# ------------- GAME ROUTES ------------- #
@app.route('/start-top-fifty-recents-game', methods=['POST'])
@cross_origin()
def start_top_fifty_game():
    data = request.get_json()
    user_id = data.get("spotify_user_id")
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    if not can_user_play_today(user_id):
        game_id = get_user_todays_game(user_id)
        existing = load_game_from_redis(game_id)
        if existing:
            response = existing.get_current_state()
            response.update({
                "game_id": game_id,
                "spotify_user_id": user_id,
                "is_existing_game": True
            })
            return jsonify(response)
        else:
            return jsonify({
                "game_id": game_id,
                "spotify_user_id": user_id,
                "message": "Game expired",
                "is_existing_game": True,
                "game_data_expired": True
            })

    sp = get_cached_spotify_session(user_id)
    if not sp:
        return jsonify({"error": "Session expired"}), 401

    deezer = Deezer()
    track_ids = list(set(sp.get_current_user_recently_played(limit=50)))
    song = None
    while track_ids:
        track_id = random.choice(track_ids)
        track_info = sp.get_track_info(track_id)
        preview = deezer.find_track_preview_url(track_info["track_name"], track_info["artist_name"])
        if preview:
            track_info['clip'] = preview
            song = Song(track_info)
            break
        track_ids.remove(track_id)

    if not song:
        return jsonify({"error": "No valid songs found"}), 400

    game = Game(song)
    game_id = str(uuid.uuid4())
    mark_user_played_today(user_id, game_id)
    save_game_to_redis(game_id, game)

    response = game.get_current_state()
    response.update({
        "game_id": game_id,
        "spotify_user_id": user_id,
        "is_existing_game": False
    })
    return jsonify(response)

@app.route('/make-guess', methods=['POST'])
@cross_origin()
def make_guess():
    data = request.get_json()
    game_id = data.get("game_id")
    guess = data.get("guess")
    if not game_id or not guess:
        return jsonify({"error": "Missing game_id or guess"}), 400

    game = load_game_from_redis(game_id)
    if not game:
        return jsonify({"error": "Game not found or expired"}), 404

    result = game.process_guess(guess)
    save_game_to_redis(game_id, game)
    return jsonify(result)

@app.route('/get-game-state', methods=['GET'])
@cross_origin()
def get_game_state():
    game_id = request.args.get("game_id")
    game = load_game_from_redis(game_id)
    if not game:
        return jsonify({"error": "Game not found or expired"}), 404
    state = game.get_current_state()
    state["game_id"] = game_id
    return jsonify(state)

@app.route('/logout-spotify', methods=['POST'])
@cross_origin()
def logout_spotify():
    try:
        for key in redis_client.keys("spotify_session:*"):
            redis_client.delete(key)
        clear_cache()
        return jsonify({"success": True, "message": "Logged out Spotify"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
