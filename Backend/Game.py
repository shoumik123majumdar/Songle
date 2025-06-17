from fuzzywuzzy import fuzz

class Game:
    def __init__(self, song):
        self.target_song_info = song
        self.guess_count = 0
        self.previous_guesses = []
        # Track revealed hints
        self.revealed_hints = {
            "genre": None,
            "release_date": None,
            "artist": None,
            "audio_snippet": None,
            "album_cover_status": "blurred",
            "full_audio_clip": None,
            "spotify_link": None
        }

    def _get_all_hints(self):
        """Helper method to get all hints"""
        return {
            "genre": self.target_song_info.get_genre(),
            "release_date": self.target_song_info.get_release_date(),
            "artist": self.target_song_info.get_artist_name(),
            "audio_snippet": self.target_song_info.get_snippet(),
            "album_cover_status": "unblur",
            "full_audio_clip": self.target_song_info.get_clip(),
            "spotify_link": self.target_song_info.get_spotify_link()
        }

    def get_current_state(self):
        """
        Get the current game state as a JSON
        """
        is_game_over, result = self._is_game_over()
        response = {
            "gameState": {
                "guessCount": self.guess_count,
                "isGameOver": is_game_over,
                "wonGame": "Won" in result if is_game_over else False,
                "correctSong": self.target_song_info.track_name
            },
            "hints": self.revealed_hints,  # Now using the updated game state
            "previousGuesses": self.previous_guesses,
            "album_cover": self.target_song_info.get_album_image()
        }
        return response
    
    def process_guess(self, guess):
        """
        Process the user's guess and return appropriate game state and hints
        """
        self.guess_count += 1
        self.previous_guesses.append(guess)
        
        # Check if this guess is correct BEFORE checking if game is over
        is_correct_guess = self._validate_user_guess(guess)
        
        # Update revealed hints based on guess count
        if self.guess_count >= 1:
            self.revealed_hints["genre"] = self.target_song_info.get_genre()
        if self.guess_count >= 2:
            self.revealed_hints["release_date"] = self.target_song_info.get_release_date()
        if self.guess_count >= 3:
            self.revealed_hints["artist"] = self.target_song_info.get_artist_name()
        if self.guess_count >= 4:
            self.revealed_hints["audio_snippet"] = self.target_song_info.get_snippet()
        if self.guess_count >= 5:
            self.revealed_hints["album_cover_status"] = "unblur"

        # Check if game is over (either won or lost)
        is_game_over = self._is_game_over_check(is_correct_guess)
        
        # If game is over, reveal all hints
        if is_game_over:
            self.revealed_hints = self._get_all_hints()
        
        # Create response using the updated game state
        response = self.get_current_state()
        return response
    
    def _is_game_over_check(self, is_correct_guess):
        """
        Helper function that determines if the game is over
        Conditions for game to be over:
            - User has guessed over 5 times
            - User has guessed song correctly
        :param is_correct_guess: boolean indicating if the current guess is correct
        :return: boolean True if game is over, False if not
        """
        # Game is over if they guessed correctly OR exceeded max guesses
        return is_correct_guess or self.guess_count > 5

    def _is_game_over(self, guess=None):
        """
        Helper function that determines if the game is over using the games state when called
        This version is used for getting current state without processing a new guess
        :param guess: user's song guess (string) - optional
        :return: tuple (boolean, string) - (is_over, result_type)
        """
        if self.guess_count > 5:
            return True, "Lost"
        elif guess and self._validate_user_guess(guess):
            return True, "Won"
        elif self.previous_guesses and self._validate_user_guess(self.previous_guesses[-1]):
            return True, "Won"
        return False, 'Ongoing'

    def _validate_user_guess(self, guess):
        """
        Helper function to validate the users guess against the target songs name
        Validation is based on fuzzy matching algorithm to allow for slight typos and some leeway
        :param guess: the user's song guess we are validating
        :return: True if guess and target song match, False if not
        """
        # Clean up both strings
        cleaned_guess = guess.lower().strip()
        cleaned_target = self.target_song_info.get_track_name().lower().strip()
    
        # Direct equality check first
        if cleaned_guess == cleaned_target:
            print("Exact match found!")
            return True
        
        # Fuzzy matching as backup
        similarity_ratio = fuzz.ratio(cleaned_guess, cleaned_target)
        print(f"Guess: '{cleaned_guess}'")
        print(f"Target: '{cleaned_target}'")
        print(f"Similarity: {similarity_ratio}")
    
        is_match = similarity_ratio >= 90
        print(f"Is match: {is_match}")
    
        return is_match