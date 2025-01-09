from fuzzywuzzy import fuzz

class Game:
    """Backend logic for a Spotle game is stored here"""
    def __init__(self,song_info):
        self.target_song_info = song_info
        self.guess_count = 0


    def process_guess(self,guess):
        """
        Processes the user's guess and advances the game state accordingly.

        This method handles the core game loop when a user submits a guess.
        It increments the guess count, checks if the game is over, and, if not,
        provides additional hints based on the number of guesses made.

        :param guess: The user's song guess (string).
        :return: A hint based on the current guess count if the game continues
            - 1st guess: song_genre 
            - 2nd guess: release_date
            - 3rd guess: artist_name
            - 4th guess: song_snippet
            - 5th guess: instruction to unblur album cover
            OR
            result: The game result if the game is over. "Game Over" if user lost, "User Won" if the user won
        """
        self.guess_count+=1
        #Check if the game is over first and foremost
        is_game_over, result = self._is_game_over(guess)
        if(is_game_over):
            return result
        else:
            if self.guess_count>0:
                return self.target_song_info.get_genre()
            elif self.guess_count>1:
                return self.target_song_info.get_release_date()
            elif self.guess_count>2:
                return self.target_song_info.get_artist_name()
            elif self.guess_count>3:
                return self.target_song_info.get_snippet()
            elif self.guess_count>4:
                return "unblur" # Replace with returning the album cover image unblurred to render in the UI

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