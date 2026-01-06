import { useGameState } from './hooks/useGameState';
import { useKeyboardVisibility } from './hooks/useKeyboardVisibility';
import { NarrativeDisplay } from './components/NarrativeDisplay';
import { CommandInput } from './components/CommandInput';
import { StatusBar } from './components/StatusBar';
import { QuickActions } from './components/QuickActions';
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

  const isKeyboardVisible = useKeyboardVisibility();

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
    <div className={`game-container ${isKeyboardVisible ? 'keyboard-visible' : ''}`}>
      <StatusBar currentRoom={currentRoom} inventory={inventory} exits={exits} />
      <NarrativeDisplay entries={narrative} isLoading={isLoading} />

      <div className="command-input-wrapper">
        <QuickActions
          onAction={sendCommand}
          disabled={isLoading}
          currentRoom={currentRoom}
        />
        <CommandInput onSubmit={sendCommand} disabled={isLoading} />
      </div>

      {error && <p className="error-message">{error}</p>}

      {isLoading && (
        <div className="loading-overlay" aria-live="polite">
          <span className="loading-text">The station contemplates...</span>
        </div>
      )}
    </div>
  );
}

export default App;
