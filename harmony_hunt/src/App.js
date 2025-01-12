import './App.css';
import LoginPage from './Login/LoginPage';
import { Routes, Route } from 'react-router-dom';
import Game from './Game/Game'

function App() {
  return (
      <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/game" element={<Game />} />
      </Routes>
  );
}

export default App;