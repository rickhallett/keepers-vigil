import { useGameState } from './hooks/useGameState';
import { NarrativeDisplay } from './components/NarrativeDisplay';
import { CommandInput } from './components/CommandInput';
import { StatusBar } from './components/StatusBar';
import './styles/game.css';

function App() {
  const {
    gameStarted,
    isLoading,
    error,
    narrative,
    currentRoom,
    inventory,
    exits,
    startNewGame,
    sendCommand,
  } = useGameState();

  if (!gameStarted) {
    return (
      <div className="game-container">
        <div className="start-screen">
          <h1>THE LAST VIGIL</h1>
          <p className="subtitle">A story of endings and beginnings</p>
          <button
            className="start-button"
            onClick={startNewGame}
            disabled={isLoading}
          >
            {isLoading ? 'Awakening...' : 'Begin'}
          </button>
          {error && <p className="error-message">{error}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="game-container">
      <StatusBar currentRoom={currentRoom} inventory={inventory} exits={exits} />
      <NarrativeDisplay entries={narrative} isLoading={isLoading} />
      <CommandInput onSubmit={sendCommand} disabled={isLoading} />
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default App;
