import { SystemHealth, TweetGenerationRequest, TweetGenerationResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export class ApiError extends Error {
  constructor(public statusCode: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function fetchHealth(): Promise<SystemHealth> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) {
      throw new ApiError(res.status, `Health check returned status: ${res.status}`);
    }
    return await res.json();
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(503, 'Backend service is offline or unreachable');
  }
}

export async function generateTweet(req: TweetGenerationRequest): Promise<TweetGenerationResponse> {
  const res = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Unknown server error' }));
    throw new ApiError(res.status, errorData.detail || `Server returned status ${res.status}`);
  }

  return res.json();
}
