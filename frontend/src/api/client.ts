/**
 * API Client for backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

/** Milliseconds between `/api/tasks/{id}` polls while a generation/refine job runs. Override with `VITE_TASK_POLL_INTERVAL_MS`. */
const DEFAULT_TASK_POLL_INTERVAL_MS = 5000;

export function getTaskPollIntervalMs(): number {
  const raw = import.meta.env.VITE_TASK_POLL_INTERVAL_MS;
  if (raw === undefined || raw === '') {
    return DEFAULT_TASK_POLL_INTERVAL_MS;
  }
  const n = Number(raw);
  if (!Number.isFinite(n)) {
    return DEFAULT_TASK_POLL_INTERVAL_MS;
  }
  return Math.min(120_000, Math.max(1000, Math.floor(n)));
}

export interface TestResponse {
  message: string;
  timestamp: string;
  status: string;
  backend_version: string;
}

export interface EchoResponse {
  echo: string;
  received_at: string;
  status: string;
}

export interface GenerateRequest {
  user_requirements: string;
  model?: string;
}

export interface GenerateResponse {
  status: string;
  message: string;
  task_id: string;
}

export interface RefineRequest {
  task_id: string;
  feedback: string;
  model?: string;
}

export interface RefineResponse {
  status: string;
  message: string;
  task_id: string;
}

export interface TaskStatusResponse {
  status: string;
  task?: {
    status: string;
    progress: number;
    logs: string[];
    result: any;
  };
  message?: string;
}

export interface ChatResponse {
  status: string;
  message: string;
  reply: string;
}

// Session API Types
export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: string | Date;
  task_id?: string;
}

export interface Session {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface SessionsResponse {
  status: string;
  sessions?: Session[];
  message?: string;
}

export interface SingleSessionResponse {
  status: string;
  session?: Session;
  message?: string;
}

export interface CreateSessionResponse {
  status: string;
  session?: Session;
  message?: string;
}

/**
 * Session APIs
 */
export async function fetchSessions(): Promise<Session[]> {
  const response = await fetch('/api/sessions');
  const data: SessionsResponse = await response.json();
  if (data.status === 'success' && data.sessions) {
    return data.sessions;
  }
  return [];
}

export async function fetchSession(sessionId: string): Promise<Session | null> {
  const response = await fetch(`/api/sessions/${sessionId}`);
  const data: SingleSessionResponse = await response.json();
  if (data.status === 'success' && data.session) {
    return data.session;
  }
  return null;
}

export async function createSession(initialMessage: string = "New Chat"): Promise<Session | null> {
  const response = await fetch('/api/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ initial_message: initialMessage })
  });
  const data: CreateSessionResponse = await response.json();
  if (data.status === 'success' && data.session) {
    return data.session;
  }
  return null;
}

export async function addMessageToSession(sessionId: string, message: Message): Promise<boolean> {
  const response = await fetch(`/api/sessions/${sessionId}/messages`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  const data = await response.json();
  return data.status === 'success';
}

/**
 * Test API connection
 */
export async function testConnection(): Promise<TestResponse> {
  const response = await fetch(`${API_BASE_URL}/test`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

/**
 * Test echo endpoint
 */
export async function testEcho(message: string): Promise<EchoResponse> {
  const response = await fetch(`${API_BASE_URL}/test/echo?message=${encodeURIComponent(message)}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

/**
 * Discuss mode: Send message to the language model
 */
export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Send user requirements to generate app
 */
export async function sendUserRequirements(requirements: string): Promise<GenerateResponse> {
  const response = await fetch('/api/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_requirements: requirements,
    }),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Send feedback to refine an existing app
 */
export async function sendRefineRequest(taskId: string, feedback: string): Promise<RefineResponse> {
  const response = await fetch('/api/refine', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      task_id: taskId,
      feedback: feedback,
    }),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Poll task status
 */
export async function pollTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  const response = await fetch(`/api/tasks/${taskId}`);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

