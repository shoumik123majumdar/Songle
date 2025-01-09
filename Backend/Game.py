from fuzzywuzzy import fuzz

class Game:
    def __init__(self, song_info):
        self.target_song_info = song_info
        self.guess_count = 0
        # Track revealed hints
        self.revealed_hints = {
            "genre": None,
            "release_date": None,
            "artist": None,
            "audio": None,
            "album_cover": None
        }

    def _get_all_hints(self):
        """Helper method to get all hints"""
        return {
            "genre": self.target_song_info.get_genre(),
            "release_date": self.target_song_info.get_release_date(),
            "artist": self.target_song_info.get_artist_name(),
            "audio": self.target_song_info.get_snippet(),
            "album_cover": self.target_song_info.get_unblurred_album_image()
        }

    def process_guess(self, guess):
        """
        Process the user's guess and return appropriate game state and hints
        """
        self.guess_count += 1
        is_game_over, result = self._is_game_over(guess)
        
        # Update revealed hints based on guess count
        if self.guess_count > 0:
            self.revealed_hints["genre"] = self.target_song_info.get_genre()
        if self.guess_count > 1:
            self.revealed_hints["release_date"] = self.target_song_info.get_release_date()
        if self.guess_count > 2:
            self.revealed_hints["artist"] = self.target_song_info.get_artist_name()
        if self.guess_count > 3:
            self.revealed_hints["audio"] = self.target_song_info.get_snippet()
        if self.guess_count > 4:
            self.revealed_hints["album_cover"] = self.target_song_info.get_unblurred_album_image()

        response = {
            "gameState": {
                "guessCount": self.guess_count,
                "isGameOver": is_game_over,
                "wonGame": False,
                "correctSong": self.target_song_info.track_name
            },
            "hints": self.revealed_hints
        }

        if is_game_over:
            if "Won" in result:  # User won
                response["gameState"]["wonGame"] = True
                response["hints"] = self._get_all_hints()  # Reveal all hints
            else:  # User lost
                response["gameState"]["wonGame"] = False
                response["hints"] = self._get_all_hints()  # Reveal all hints
        
        return response

    def _is_game_over(self,guess):
        """
        Helper function that determines if the game is over using the games state when the function is called
        Conditions for game to be over
            - User has guessed over 5 times
            - User has guessed song correctly
        :param guess: user's song guess (string)
        :return: boolean True if game is over, False if not
        """
        if self.guess_count>5:
            return True,"Game Over"
        elif self._validate_user_guess(guess):
            return True, f"User Won in {self.guess_count} tries"
        return False

    def _validate_user_guess(self,guess):
        """
        Helper function to validate the users guess against the target songs name
        Validation is based on fuzzy matching algorithm to allow for slight typos and some leeway
        :param guess: the user's song guess we are validating
        :return: True if guess and target song match, False if not
        """
        similarity_ratio = fuzz.ratio(guess.lower(), self.target_song_info.get_track_name().lower())

        return similarity_ratio >= 90