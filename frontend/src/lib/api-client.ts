/**
 * API client for communicating with FastAPI backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { ChatRequest, ChatResponse } from '@/types/chat';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error);

        if (error.response) {
          // Server responded with error
          throw new Error(
            `API Error: ${error.response.status} - ${JSON.stringify(error.response.data)}`
          );
        } else if (error.request) {
          // Request made but no response
          throw new Error('No response from server. Please check your connection.');
        } else {
          // Error setting up request
          throw new Error(`Request error: ${error.message}`);
        }
      }
    );
  }

  /**
   * Send a chat message
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>(
      '/api/v1/chat/message',
      request
    );
    return response.data;
  }

  /**
   * Get conversation history
   */
  async getConversation(conversationId: string): Promise<any> {
    const response = await this.client.get(
      `/api/v1/chat/conversation/${conversationId}`
    );
    return response.data;
  }

  /**
   * Create a new conversation
   */
  async createConversation(data: {
    name?: string;
    email?: string;
    phone?: string;
    platform?: string;
  }): Promise<any> {
    const response = await this.client.post(
      '/api/v1/chat/conversation',
      data
    );
    return response.data;
  }

  /**
   * Resolve identity
   */
  async resolveIdentity(data: {
    name?: string;
    email?: string;
    phone?: string;
    platform?: string;
    context?: string;
  }): Promise<any> {
    const response = await this.client.post(
      '/api/v1/identity/resolve',
      data
    );
    return response.data;
  }

  /**
   * Get escalations
   */
  async getEscalations(params?: {
    status?: string;
    priority?: string;
    limit?: number;
  }): Promise<any> {
    const response = await this.client.get('/api/v1/escalations', { params });
    return response.data;
  }

  /**
   * Get analytics stats
   */
  async getStats(): Promise<any> {
    const response = await this.client.get('/api/v1/analytics/stats');
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();
