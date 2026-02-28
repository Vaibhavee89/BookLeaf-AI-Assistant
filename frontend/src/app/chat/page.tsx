/**
 * Main chat page
 */

'use client';

import React, { useState } from 'react';
import { ChatContainer } from '@/components/chat/ChatContainer';
import { IdentityForm } from '@/components/chat/IdentityForm';
import { UserIdentity } from '@/types/chat';

export default function ChatPage() {
  const [userIdentity, setUserIdentity] = useState<UserIdentity | null>(null);

  const handleIdentitySubmit = (identity: UserIdentity) => {
    setUserIdentity(identity);
  };

  const handleResetIdentity = () => {
    setUserIdentity(null);
  };

  // Show identity form if not yet captured
  if (!userIdentity) {
    return <IdentityForm onSubmit={handleIdentitySubmit} />;
  }

  // Show chat interface
  return (
    <ChatContainer
      userIdentity={userIdentity}
      onResetIdentity={handleResetIdentity}
    />
  );
}
