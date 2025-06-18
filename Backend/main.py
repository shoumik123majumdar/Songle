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
import glob
from datetime import datetime, timedelta

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
    decode_responses=False
)

def can_user_play_today(spotify_user_id):
    """Check if this Spotify user has played today"""
    today = datetime.now().strftime('%Y-%m-%d')
    play_key = f"user_play:{spotify_user_id}:{today}"
    
    try:
        return not redis_client.exists(play_key)
    except Exception as e:
        print(f"Error checking user play status: {e}")
        return True  # Allow play if Redis is down

def mark_user_played_today(spotify_user_id):
    """Mark that this Spotify user has played today"""
    today = datetime.now().strftime('%Y-%m-%d')
    play_key = f"user_play:{spotify_user_id}:{today}"
    
    try:
        # Set expiration to end of day + 1 hour buffer
        tomorrow = datetime.now().replace(hour=23, minute=59, second=59) + timedelta(hours=1)
        seconds_until_tomorrow = int((tomorrow - datetime.now()).total_seconds())
        redis_client.setex(play_key, seconds_until_tomorrow, "played")
        return True
    except Exception as e:
        print(f"Error marking user play status: {e}")
        return False

def get_spotify_session(force_reauth=False):
    """Get or create Spotify session"""
    
    try:
        if not force_reauth:
            # Try to use any existing valid session from recent authentications
            # In a real app, you might want to check multiple recent sessions
            # For now, we'll just proceed to create a new session
            pass
        
        # Create new session
        CLIENT_ID = os.environ.get("CLIENT_ID")
        CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
        SCOPE = "user-read-playback-state user-top-read user-read-recently-played"
        
        # Generate unique session ID for this authentication
        import time
        session_id = f"session_{int(time.time())}"
        
        sp = Spotipy(CLIENT_ID, CLIENT_SECRET, SCOPE, session_id=session_id)
        sp.authenticate_user()  # This will open browser for Spotify login
        
        # Cache session using the Spotify user ID as key (1 hour expiration)
        session_key = f"spotify_session:{sp.USER_ID}"
        redis_client.setex(session_key, 3600, pickle.dumps(sp))
        return sp
        
    except Exception as e:
        print(f"Error getting Spotify session: {e}")
        raise Exception("Failed to authenticate with Spotify")

def get_current_spotify_user():
    """Get currently authenticated Spotify user (if any)"""
    try:
        # Look for any active Spotify sessions in Redis
        # This is a simple approach - in production you might track this differently
        keys = redis_client.keys("spotify_session:*")
        
        for key in keys:
            try:
                session_data = redis_client.get(key)
                if session_data:
                    sp = pickle.loads(session_data)
                    # Test if session is still valid
                    user_info = sp.sp.current_user()
                    return {
                        "spotify_user_id": sp.USER_ID,
                        "display_name": user_info.get('display_name', 'Unknown'),
                        "is_authenticated": True
                    }
            except:
                # This session is invalid, remove it
                redis_client.delete(key)
                continue
                
        return {"is_authenticated": False}
        
    except Exception as e:
        print(f"Error checking current user: {e}")
        return {"is_authenticated": False}

def clear_cache():
    """Clear cookie cache - removes all .cache files"""
    try:
        cache_files = glob.glob(".cache*")
        for cache_file in cache_files:
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print(f"Removed cache file: {cache_file}")
    except Exception as e:
        print(f"Error clearing cache: {e}")

def save_game_to_redis(game_id, game_obj):
    """Serialize and save game object to Redis with 24-hour expiration"""
    try:
        serialized_game = pickle.dumps(game_obj)
        redis_client.setex(f"game:{game_id}", 86400, serialized_game)
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

@app.route('/spotify-login', methods=['POST'])
@cross_origin()
def spotify_login():
    """Initiate Spotify authentication - always creates new session"""
    try:
        clear_cache()  # Clear any old cache files
        
        # Force new authentication
        sp = get_spotify_session(force_reauth=True)
        
        return jsonify({
            "success": True,
            "spotify_user_id": sp.USER_ID,
            "spotify_display_name": sp.sp.current_user().get('display_name', 'Unknown'),
            "message": "Successfully authenticated with Spotify"
        })
        
    except Exception as e:
        print(f"Error during Spotify login: {e}")
        return jsonify({"error": "Failed to authenticate with Spotify"}), 500

@app.route('/current-user', methods=['GET'])
@cross_origin()
def current_user():
    """Get current authenticated Spotify user info"""
    try:
        user_info = get_current_spotify_user()
        return jsonify(user_info)
        
    except Exception as e:
        print(f"Error getting current user: {e}")
        return jsonify({"error": "Failed to get user info"}), 500

@app.route('/check-play-status', methods=['GET'])
@cross_origin()
def check_play_status():
    """Check if current authenticated user can play today"""
    try:
        user_info = get_current_spotify_user()
        
        if not user_info["is_authenticated"]:
            return jsonify({
                "error": "No Spotify user authenticated",
                "needs_spotify_auth": True
            }), 401
        
        spotify_user_id = user_info["spotify_user_id"]
        can_play = can_user_play_today(spotify_user_id)
        
        response = {
            "can_play": can_play,
            "spotify_user_id": spotify_user_id,
            "spotify_display_name": user_info["display_name"]
        }
        
        if not can_play:
            next_play = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0)
            response["next_play_time"] = next_play.isoformat()
            response["message"] = f"You've already played today! Come back tomorrow."
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error checking play status: {e}")
        return jsonify({"error": "Failed to check play status"}), 500

@app.route('/start-top-fifty-recents-game', methods=['POST'])
@cross_origin()
def start_top_fifty_game():
    try:
        # Check if user is authenticated
        user_info = get_current_spotify_user()
        
        if not user_info["is_authenticated"]:
            return jsonify({
                "error": "No Spotify user authenticated. Please login first.",
                "needs_spotify_auth": True
            }), 401
        
        spotify_user_id = user_info["spotify_user_id"]
        
        # Check if this Spotify account can play today
        if not can_user_play_today(spotify_user_id):
            next_play = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0)
            return jsonify({
                "error": f"You've already played today! Come back tomorrow or login with a different Spotify account.",
                "can_play": False,
                "next_play_time": next_play.isoformat(),
                "spotify_user_id": spotify_user_id
            }), 429
        
        # Get the cached Spotify session
        session_key = f"spotify_session:{spotify_user_id}"
        session_data = redis_client.get(session_key)
        if not session_data:
            return jsonify({
                "error": "Spotify session expired. Please login again.",
                "needs_spotify_auth": True
            }), 401
            
        sp = pickle.loads(session_data)
        deezer = Deezer()
        
        recently_played_track_id_list = list(set(sp.get_current_user_recently_played(limit=50)))
        song = None

        # Find a song with preview
        while True:
            if len(recently_played_track_id_list) == 0:
                return jsonify({
                    "error": "Not enough recent tracks (or no song data could be found for them). Listen to more music and come back!"
                }), 400
        
            song_index = random.randint(0, len(recently_played_track_id_list) - 1)  
            chosen_track_id = recently_played_track_id_list[song_index]
            track_info = sp.get_track_info(chosen_track_id)
            preview_url = deezer.find_track_preview_url(track_info["track_name"], track_info["artist_name"])
            
            if preview_url:
                track_info['clip'] = preview_url
                song = Song(track_info)
                break
            else:
                recently_played_track_id_list.pop(song_index)
        
        # Create game
        game = Game(song)
        game_id = str(uuid.uuid4())
        
        # Mark this Spotify account as having played today
        mark_user_played_today(spotify_user_id)
        
        # Save game to Redis
        save_game_to_redis(game_id, game)
        
        response = game.get_current_state()
        response["game_id"] = game_id
        response["spotify_user_id"] = spotify_user_id
        response["spotify_display_name"] = user_info["display_name"]
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error starting game: {e}")
        return jsonify({"error": "Failed to start game. Please try again."}), 500

@app.route('/make-guess', methods=['POST'])
@cross_origin()
def make_guess():
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        guess = data.get('guess')
        
        if not game_id or not guess:
            return jsonify({"error": "Missing game_id or guess"}), 400
        
        # Load game from Redis
        game = load_game_from_redis(game_id)
        if not game:
            return jsonify({"error": "Game not found or expired"}), 404
        
        # Process the guess
        response = game.process_guess(guess)
        
        # Save updated game state
        save_game_to_redis(game_id, game)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error processing guess: {e}")
        return jsonify({"error": "Failed to process guess. Please try again."}), 500

@app.route('/get-game-state', methods=['GET'])
@cross_origin()
def get_game_state():
    try:
        game_id = request.args.get('game_id')
        if not game_id:
            return jsonify({"error": "No game_id provided"}), 400
        
        game = load_game_from_redis(game_id)
        if not game:
            return jsonify({"error": "Game not found or expired"}), 404
        
        response = game.get_current_state()
        response["game_id"] = game_id
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error getting game state: {e}")
        return jsonify({"error": "Failed to get game state. Please try again."}), 500

@app.route('/logout-spotify', methods=['POST'])
@cross_origin()
def logout_spotify():
    """Clear Spotify session to allow re-authentication with different account"""
    try:
        # Clear all active sessions and cache files
        clear_cache()  # Clear local cache files
        
        # Also clear Redis sessions (optional - they'll expire anyway)
        try:
            keys = redis_client.keys("spotify_session:*")
            if keys:
                redis_client.delete(*keys)
        except Exception as e:
            print(f"Error clearing Redis sessions: {e}")
        
        return jsonify({
            "message": "Spotify session cleared. You can now authenticate with a different account.",
            "success": True
        })
        
    except Exception as e:
        print(f"Error logging out Spotify: {e}")
        return jsonify({"error": "Failed to logout"}), 500

if __name__ == '__main__':
    app.run(debug=True)