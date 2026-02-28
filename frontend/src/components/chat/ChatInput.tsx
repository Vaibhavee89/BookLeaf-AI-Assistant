/**
 * Chat input component with identity capture
 */

import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = 'Type your message...',
}) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className={cn(
          'w-full px-4 py-3 pr-12 rounded-2xl border border-gray-300',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
          'resize-none text-sm',
          'disabled:bg-gray-100 disabled:cursor-not-allowed',
          'transition-all duration-200'
        )}
        style={{
          minHeight: '48px',
          maxHeight: '150px',
        }}
      />

      {/* Send button */}
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className={cn(
          'absolute right-2 bottom-2 p-2 rounded-full',
          'bg-primary-500 text-white',
          'hover:bg-primary-600 active:bg-primary-700',
          'disabled:bg-gray-300 disabled:cursor-not-allowed',
          'transition-all duration-200',
          'flex items-center justify-center'
        )}
        aria-label="Send message"
      >
        {disabled ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : (
          <Send className="w-5 h-5" />
        )}
      </button>
    </form>
  );
};
