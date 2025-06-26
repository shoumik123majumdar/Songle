import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LoginPage from './Login/LoginPage';
import CallbackHandler from './Login/CallbackHandler';
import Game from './Game/Game';

function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage/>} />
      <Route path="/callback" element={<CallbackHandler />} />
      <Route path="/game" element={<Game />} />
    </Routes>
  );
}

export default App;