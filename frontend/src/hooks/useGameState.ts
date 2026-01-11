import { useState, useCallback, useRef, useEffect } from 'react';
import { api, isApiError } from '../api/client';
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

// Error message mapping for user-friendly messages
function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    switch (error.status) {
      case 429:
        return 'Too many requests. Please wait a moment before trying again.';
      case 404:
        return 'Session not found. Please start a new game.';
      case 500:
        return 'The station experiences a momentary disturbance. Please try again.';
      default:
        return error.message || 'Something went wrong.';
    }
  }
  return error instanceof Error ? error.message : 'An unexpected error occurred.';
}

export function useGameState() {
  const [state, setState] = useState<GameState>(initialState);

  // Use refs to avoid stale closures
  const sessionIdRef = useRef<string | null>(null);
  const isLoadingRef = useRef(false);
  const errorTimeoutRef = useRef<number | undefined>(undefined);

  // Keep refs in sync with state
  useEffect(() => {
    sessionIdRef.current = state.sessionId;
    isLoadingRef.current = state.isLoading;
  }, [state.sessionId, state.isLoading]);

  // Auto-dismiss errors after 5 seconds
  useEffect(() => {
    if (state.error) {
      errorTimeoutRef.current = window.setTimeout(() => {
        setState((prev) => ({ ...prev, error: null }));
      }, 5000);
    }
    return () => {
      if (errorTimeoutRef.current) {
        window.clearTimeout(errorTimeoutRef.current);
      }
    };
  }, [state.error]);

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
        error: getErrorMessage(err),
      }));
    }
  }, []);

  const sendCommand = useCallback(async (input: string) => {
    // Use refs to avoid stale closure issues
    if (!sessionIdRef.current || isLoadingRef.current) return;

    // Add player input to narrative
    addNarrative(`> ${input}`, 'player');

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const response: CommandResponse = await api.sendCommand(sessionIdRef.current, input);

      setState((prev) => ({
        ...prev,
        currentRoom: response.current_room,
        inventory: response.inventory,
        exits: response.exits,
        isLoading: false,
      }));

      addNarrative(response.narrative, 'narrator');
    } catch (err) {
      const errorMessage = getErrorMessage(err);

      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));

      // Only add narrative error for non-rate-limit errors
      if (!isApiError(err) || err.status !== 429) {
        addNarrative('Something went wrong. Please try again.', 'narrator');
      }
    }
  }, [addNarrative]);

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
