/**
 * Individual chat message component
 */

import React from 'react';
import { cn, formatTime } from '@/lib/utils';
import { Message } from '@/types/chat';
import { Bot, User } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
  showTimestamp?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  showTimestamp = true,
}) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <div
      className={cn(
        'flex gap-3 mb-4',
        isUser && 'flex-row-reverse'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-700'
        )}
      >
        {isUser ? (
          <User className="w-5 h-5" />
        ) : (
          <Bot className="w-5 h-5" />
        )}
      </div>

      {/* Message content */}
      <div className={cn('flex-1 max-w-[80%]', isUser && 'flex flex-col items-end')}>
        {/* Message bubble */}
        <div
          className={cn(
            'rounded-2xl px-4 py-3 shadow-sm',
            isUser
              ? 'bg-primary-500 text-white rounded-tr-none'
              : 'bg-white border border-gray-200 rounded-tl-none'
          )}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
            {message.content}
          </p>
        </div>

        {/* Timestamp and metadata */}
        {showTimestamp && message.created_at && (
          <div className={cn(
            'flex items-center gap-2 mt-1 px-1',
            isUser ? 'justify-end' : 'justify-start'
          )}>
            <span className="text-xs text-gray-500">
              {formatTime(message.created_at)}
            </span>
            {message.intent && isAssistant && (
              <>
                <span className="text-gray-300">•</span>
                <span className="text-xs text-gray-500 capitalize">
                  {message.intent.replace('_', ' ')}
                </span>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
