/**
 * Main chat container component
 */

'use client';

import React, { useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ConfidenceIndicator } from './ConfidenceIndicator';
import { useChat } from '@/hooks/useChat';
import { UserIdentity } from '@/types/chat';
import { cn, getDisplayName } from '@/lib/utils';
import { Bot, RefreshCw, AlertCircle } from 'lucide-react';

interface ChatContainerProps {
  userIdentity: UserIdentity;
  onResetIdentity?: () => void;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  userIdentity,
  onResetIdentity,
}) => {
  const {
    messages,
    isLoading,
    error,
    conversationId,
    lastResponse,
    sendMessage,
    clearError,
    resetChat,
  } = useChat(userIdentity);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleReset = () => {
    if (window.confirm('Are you sure you want to start a new conversation?')) {
      resetChat();
      if (onResetIdentity) {
        onResetIdentity();
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 shadow-sm">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                BookLeaf AI Assistant
              </h1>
              <p className="text-sm text-gray-500">
                Chatting as {getDisplayName(userIdentity.name, userIdentity.email)}
              </p>
            </div>
          </div>

          <button
            onClick={handleReset}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Reset conversation"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {/* Welcome message */}
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
                <Bot className="w-8 h-8 text-primary-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Welcome to BookLeaf AI Assistant!
              </h2>
              <p className="text-gray-600 max-w-md mx-auto">
                I&apos;m here to help you with questions about publishing, royalties,
                your author dashboard, and more. How can I assist you today?
              </p>

              {/* Quick prompts */}
              <div className="mt-8 space-y-2 max-w-md mx-auto">
                <p className="text-sm font-medium text-gray-700 mb-3">
                  Try asking:
                </p>
                {[
                  'When will my royalty payment be processed?',
                  'How does the publishing process work?',
                  'What premium services do you offer?',
                  'How do I access my author dashboard?',
                ].map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(prompt)}
                    className="block w-full text-left px-4 py-3 bg-white border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-sm"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((message, index) => (
            <ChatMessage
              key={index}
              message={message}
              showTimestamp={true}
            />
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-gray-700" />
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </div>
          )}

          {/* Confidence indicator (after assistant response) */}
          {lastResponse && messages.length > 0 && messages[messages.length - 1].role === 'assistant' && (
            <div className="mb-4 flex justify-start">
              <div className="max-w-[80%]">
                <ConfidenceIndicator
                  confidence={lastResponse.confidence}
                  breakdown={lastResponse.confidence_breakdown}
                  showDetails={true}
                />

                {/* Metadata info */}
                <div className="mt-2 text-xs text-gray-500 space-y-1">
                  <p>
                    <span className="font-medium">Processing time:</span>{' '}
                    {lastResponse.metadata.processing_time_ms}ms
                  </p>
                  <p>
                    <span className="font-medium">Identity method:</span>{' '}
                    {lastResponse.metadata.identity_method.replace('_', ' ')}
                  </p>
                  {conversationId && (
                    <p className="font-mono text-[10px]">
                      Conversation: {conversationId.slice(0, 8)}...
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="mb-4 flex items-start gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-red-900">Error</p>
                <p className="text-red-700 text-sm mt-1">{error}</p>
                <button
                  onClick={clearError}
                  className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
                >
                  Dismiss
                </button>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="bg-white border-t border-gray-200 px-4 py-4 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <ChatInput
            onSendMessage={sendMessage}
            disabled={isLoading}
            placeholder={
              isLoading
                ? 'Please wait...'
                : 'Type your message... (Press Enter to send, Shift+Enter for new line)'
            }
          />
        </div>
      </div>
    </div>
  );
};
