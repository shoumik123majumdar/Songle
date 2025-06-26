import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const CallbackHandler = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');

      if (!code) {
        alert('Missing Spotify authorization code.');
        navigate('/');
        return;
      }

      try {
        // Step 1: Exchange code for tokens and get user info
        console.log('Exchanging code for tokens...');
        const authResponse = await axios.post('http://127.0.0.1:5000/exchange-code', {
          code: code,
          state: state
        });

        const { spotify_user_id, display_name } = authResponse.data;
        
        // Store user info
        localStorage.setItem('spotify_user_id', spotify_user_id);
        localStorage.setItem('spotify_display_name', display_name);
        
        console.log('Successfully authenticated user:', spotify_user_id);

        // Step 2: Start the game
        console.log('Starting game...');
        const gameResponse = await axios.post('http://127.0.0.1:5000/start-top-fifty-recents-game', {
          spotify_user_id: spotify_user_id
        });

        const { game_id, album_cover, is_existing_game, game_data_expired } = gameResponse.data;
        
        // Store game ID
        localStorage.setItem('harmony_hunt_game_id', game_id);
        
        console.log('Game started:', { game_id, is_existing_game });

        // Navigate to game
        navigate('/game', {
          state: {
            gameId: game_id,
            albumURL: album_cover
          },
          replace: true
        });

      } catch (error) {
        console.error('Authentication or game start failed:', error);
        
        if (error.response) {
          const status = error.response.status;
          const errorMsg = error.response.data.error || 'An error occurred';
          
          if (status === 401) {
            alert('Authentication failed. Please try again.');
          } else if (status === 400) {
            alert(errorMsg);
          } else {
            alert('Failed to complete login. Please try again.');
          }
        } else {
          alert('Network error. Please check your connection.');
        }
        
        navigate('/');
      }
    };

    handleCallback();
  }, [navigate]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      fontSize: '18px',
      color: '#666'
    }}>
      Completing Spotify login...
    </div>
  );
};

export default CallbackHandler;