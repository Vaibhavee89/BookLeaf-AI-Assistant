/**
 * TypeScript types for chat functionality
 */

export interface Message {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  confidence?: number;
  intent?: string;
  created_at?: string;
}

export interface ConfidenceFactor {
  score: number;
  weight: number;
  contribution: number;
}

export interface ConfidenceBreakdown {
  overall_confidence: number;
  action: 'auto_respond' | 'escalate';
  factors: {
    identity: ConfidenceFactor;
    intent: ConfidenceFactor;
    rag: ConfidenceFactor;
    llm: ConfidenceFactor;
  };
  threshold: number;
  weakest_factor: {
    name: string;
    score: number;
  };
}

export interface Escalation {
  id: string;
  conversation_id: string;
  reason: string;
  priority: string;
  status: string;
  created_at: string;
}

export interface ChatResponse {
  success: boolean;
  response: string;
  confidence: number;
  confidence_breakdown: ConfidenceBreakdown;
  should_escalate: boolean;
  escalation?: Escalation;
  metadata: {
    conversation_id: string;
    author_id: string;
    identity_id: string;
    identity_confidence: number;
    identity_method: string;
    intent: string;
    intent_confidence: number;
    processing_time_ms: number;
    llm_model: string;
    tokens_used: number;
  };
}

export interface ChatRequest {
  message: string;
  name?: string;
  email?: string;
  phone?: string;
  platform?: string;
  conversation_id?: string;
}

export interface UserIdentity {
  name: string;
  email: string;
  phone?: string;
}
