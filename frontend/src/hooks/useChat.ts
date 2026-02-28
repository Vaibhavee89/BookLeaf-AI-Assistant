/**
 * Custom hook for chat functionality
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import { Message, ChatResponse, UserIdentity } from '@/types/chat';

export interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  lastResponse: ChatResponse | null;
  sendMessage: (content: string) => Promise<void>;
  clearError: () => void;
  resetChat: () => void;
}

export function useChat(userIdentity: UserIdentity): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      setError(null);
      setIsLoading(true);

      // Add user message immediately
      const userMessage: Message = {
        role: 'user',
        content: content.trim(),
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);

      try {
        // Send to API
        const response = await apiClient.sendMessage({
          message: content.trim(),
          name: userIdentity.name,
          email: userIdentity.email,
          phone: userIdentity.phone,
          conversation_id: conversationId || undefined,
        });

        // Store conversation ID
        if (response.metadata.conversation_id && !conversationId) {
          setConversationId(response.metadata.conversation_id);
        }

        // Add assistant response
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.response,
          confidence: response.confidence,
          intent: response.metadata.intent,
          created_at: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
        setLastResponse(response);

      } catch (err) {
        console.error('Failed to send message:', err);
        setError(err instanceof Error ? err.message : 'Failed to send message');

        // Add error message
        const errorMessage: Message = {
          role: 'assistant',
          content: 'I apologize, but I encountered an error processing your message. Please try again.',
          created_at: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, conversationId, userIdentity]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const resetChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setLastResponse(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    conversationId,
    lastResponse,
    sendMessage,
    clearError,
    resetChat,
  };
}
