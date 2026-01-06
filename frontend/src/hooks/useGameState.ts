import { useState, useCallback } from 'react';
import { api } from '../api/client';
import type { NewGameResponse, CommandResponse } from '../api/client';

export interface NarrativeEntry {
  id: number;
  text: string;
  type: 'narrator' | 'player';
  timestamp: number;
}

export interface GameState {
  sessionId: string | null;
  currentRoom: string;
  inventory: string[];
  exits: string[];
  narrative: NarrativeEntry[];
  isLoading: boolean;
  error: string | null;
  gameStarted: boolean;
}

const initialState: GameState = {
  sessionId: null,
  currentRoom: 'threshold',
  inventory: [],
  exits: [],
  narrative: [],
  isLoading: false,
  error: null,
  gameStarted: false,
};

let entryId = 0;

export function useGameState() {
  const [state, setState] = useState<GameState>(initialState);

  const addNarrative = useCallback((text: string, type: 'narrator' | 'player') => {
    setState((prev) => ({
      ...prev,
      narrative: [
        ...prev.narrative,
        {
          id: ++entryId,
          text,
          type,
          timestamp: Date.now(),
        },
      ],
    }));
  }, []);

  const startNewGame = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const response: NewGameResponse = await api.newGame();

      setState({
        sessionId: response.session_id,
        currentRoom: response.current_room,
        inventory: response.inventory,
        exits: response.exits,
        narrative: [
          {
            id: ++entryId,
            text: response.narrative,
            type: 'narrator',
            timestamp: Date.now(),
          },
        ],
        isLoading: false,
        error: null,
        gameStarted: true,
      });
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to start game',
      }));
    }
  }, []);

  const sendCommand = useCallback(async (input: string) => {
    if (!state.sessionId || state.isLoading) return;

    // Add player input to narrative
    addNarrative(`> ${input}`, 'player');

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const response: CommandResponse = await api.sendCommand(state.sessionId, input);

      setState((prev) => ({
        ...prev,
        currentRoom: response.current_room,
        inventory: response.inventory,
        exits: response.exits,
        isLoading: false,
      }));

      addNarrative(response.narrative, 'narrator');
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to process command',
      }));

      addNarrative('Something went wrong. Please try again.', 'narrator');
    }
  }, [state.sessionId, state.isLoading, addNarrative]);

  const resetGame = useCallback(() => {
    setState(initialState);
    entryId = 0;
  }, []);

  return {
    ...state,
    startNewGame,
    sendCommand,
    resetGame,
  };
}
