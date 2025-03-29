/**
 * API utilities for communicating with the Flask backend
 */

// Default API URL (should be overridden by environment variable)
const API_URL = process.env.NEXT_PUBLIC_FLASK_API_URL || 'http://localhost:5000';

/**
 * Interface for API responses
 */
interface ApiResponse<T = any> {
  data?: T;
  error?: string;
}

/**
 * Send a request to the Flask backend API
 */
export async function fetchFromFlask<T = any>(
  endpoint: string,
  options: {
    method?: 'GET' | 'POST' | 'DELETE';
    body?: any;
  } = {}
): Promise<ApiResponse<T>> {
  const { method = 'GET', body } = options;
  
  try {
    console.log(`Making API request to: ${API_URL}/api/${endpoint}`);
    const response = await fetch(`${API_URL}/api/${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
      credentials: 'include', // Include cookies for session management
    });

    // Attempt to parse JSON response
    let data;
    try {
      data = await response.json();
    } catch (error) {
      console.error('Failed to parse JSON response:', error);
      return { error: 'Invalid response format from server' };
    }
    
    if (!response.ok) {
      console.error('API error response:', data);
      return { error: data.error || `Error ${response.status}: ${response.statusText}` };
    }
    
    return { data };
  } catch (error) {
    console.error('API fetch error:', error);
    return { 
      error: error instanceof Error 
        ? `Connection error: ${error.message}` 
        : 'Failed to connect to the server' 
    };
  }
}

/**
 * API client for specific endpoints
 */
export const api = {
  // Scenario endpoints
  scenarios: {
    getAll: () => fetchFromFlask('scenarios'),
    create: (name: string) => fetchFromFlask('scenarios', { 
      method: 'POST', 
      body: { name } 
    }),
    delete: (name: string) => fetchFromFlask(`scenarios/${name}`, { 
      method: 'DELETE'
    }),
  },
  
  // Game session endpoints
  game: {
    start: (scenario: string) => fetchFromFlask('start', { 
      method: 'POST', 
      body: { scenario } 
    }),
    makeDecision: (sceneId: number, decision: string) => fetchFromFlask('decision', { 
      method: 'POST', 
      body: { scene_id: sceneId, decision } 
    }),
    getProgress: () => fetchFromFlask('progress'),
  }
}; 