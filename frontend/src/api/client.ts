const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface NewGameResponse {
  session_id: string;
  narrative: string;
  current_room: string;
  inventory: string[];
  exits: string[];
}

export interface CommandResponse {
  narrative: string;
  current_room: string;
  inventory: string[];
  exits: string[];
  state_changed: boolean;
}

export interface StateResponse {
  current_room: string;
  inventory: string[];
  available_exits: string[];
  available_objects: string[];
  available_characters: string[];
}

export interface ApiError {
  status: number;
  message: string;
}

function createApiError(status: number, message: string): ApiError & Error {
  const error = new Error(message) as ApiError & Error;
  error.status = status;
  error.name = 'ApiError';
  return error;
}

function isApiError(error: unknown): error is ApiError & Error {
  return error instanceof Error && 'status' in error;
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw createApiError(response.status, errorBody.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  newGame: () => request<NewGameResponse>('/api/new-game', { method: 'POST' }),

  sendCommand: (sessionId: string, input: string) =>
    request<CommandResponse>('/api/command', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, input }),
    }),

  getState: (sessionId: string) =>
    request<StateResponse>(`/api/state/${sessionId}`),

  healthCheck: () => request<{ status: string }>('/api/health'),
};

export { isApiError };
