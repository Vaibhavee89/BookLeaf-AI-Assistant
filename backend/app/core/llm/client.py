"""OpenAI LLM client with model routing and retry logic."""

from typing import List, Dict, Any, Optional
import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import structlog
import tiktoken

from app.config import settings

logger = structlog.get_logger(__name__)


class LLMClient:
    """Client for interacting with OpenAI models with intelligent routing and fallback."""

    def __init__(self):
        """Initialize the LLM client."""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

        # Model configuration
        self.primary_model = settings.primary_model  # gpt-4-turbo-preview
        self.fallback_model = settings.fallback_model  # gpt-4
        self.classification_model = settings.classification_model  # gpt-4o-mini

        # Token encoding
        self.encoding = tiktoken.encoding_for_model("gpt-4")

        logger.info(
            "llm_client_initialized",
            primary_model=self.primary_model,
            fallback_model=self.fallback_model,
            classification_model=self.classification_model
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError))
    )
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        use_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Get chat completion with automatic fallback on failure.

        Args:
            messages: List of message dictionaries
            model: Model to use (default: primary_model)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            response_format: Response format specification (e.g., {"type": "json_object"})
            use_fallback: Whether to fallback to secondary model on failure

        Returns:
            Dictionary with response text, model used, and token counts
        """
        model_to_use = model or self.primary_model

        try:
            logger.debug(
                "chat_completion_request",
                model=model_to_use,
                messages_count=len(messages),
                temperature=temperature
            )

            # Make API call
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )

            result = {
                "content": response.choices[0].message.content,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

            logger.info(
                "chat_completion_success",
                model=result["model"],
                tokens=result["usage"]["total_tokens"],
                finish_reason=result["finish_reason"]
            )

            return result

        except (openai.RateLimitError, openai.APIError) as e:
            logger.warning(
                "chat_completion_error_retrying",
                model=model_to_use,
                error=str(e)
            )
            # Let tenacity retry decorator handle this
            raise

        except Exception as e:
            logger.error(
                "chat_completion_failed",
                model=model_to_use,
                error=str(e),
                exc_info=e
            )

            # Try fallback model if enabled and not already using it
            if use_fallback and model_to_use != self.fallback_model:
                logger.info("attempting_fallback_model", fallback=self.fallback_model)

                try:
                    return self.chat_completion(
                        messages=messages,
                        model=self.fallback_model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_format=response_format,
                        use_fallback=False  # Prevent infinite recursion
                    )
                except Exception as fallback_error:
                    logger.error(
                        "fallback_model_also_failed",
                        error=str(fallback_error)
                    )
                    raise

            raise

    def classify_intent(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Classify user intent using classification model.

        Args:
            user_message: User's message
            conversation_history: Previous messages for context

        Returns:
            Dictionary with intent and confidence
        """
        system_prompt = """You are an intent classification system for a publishing company's customer support.

Classify the user's query into ONE of these intents:
- author_specific: Questions about their specific account, books, payments, or personal data
- general_knowledge: Questions about publishing process, royalties, services, or policies
- technical_support: Issues with website, dashboard, login, or technical problems
- out_of_scope: Questions unrelated to publishing or the company

Respond with JSON: {"intent": "intent_name", "confidence": 0.0-1.0, "reasoning": "brief explanation"}"""

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            messages.extend(conversation_history[-3:])  # Last 3 messages for context

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.chat_completion(
                messages=messages,
                model=self.classification_model,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response["content"])

            logger.info(
                "intent_classified",
                intent=result.get("intent"),
                confidence=result.get("confidence")
            )

            return result

        except Exception as e:
            logger.error("intent_classification_failed", error=str(e))
            # Return default classification
            return {
                "intent": "general_knowledge",
                "confidence": 0.5,
                "reasoning": f"Classification failed: {str(e)}"
            }

    def generate_response(
        self,
        user_message: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response to user message with optional RAG context.

        Args:
            user_message: User's message
            context: RAG context from knowledge base
            conversation_history: Previous messages
            system_prompt: Custom system prompt
            model: Model to use

        Returns:
            Generated response with metadata
        """
        # Default system prompt
        if not system_prompt:
            system_prompt = """You are a helpful AI assistant for BookLeaf Publishing.
You help authors with questions about publishing, royalties, services, and their accounts.
Be friendly, professional, and concise.
If you don't know something, say so honestly."""

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages

        # Add RAG context if provided
        if context:
            context_message = f"""Here is relevant information from our knowledge base:

{context}

Use this information to answer the user's question. If the information doesn't fully answer their question, use your general knowledge but note that they may need to contact support for specific details."""
            messages.append({"role": "system", "content": context_message})

        # Add user message
        messages.append({"role": "user", "content": user_message})

        return self.chat_completion(
            messages=messages,
            model=model,
            temperature=0.7
        )

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count total tokens in message list.

        Args:
            messages: List of messages

        Returns:
            Total token count
        """
        total = 0
        for message in messages:
            # Count role and content
            total += len(self.encoding.encode(message.get("role", "")))
            total += len(self.encoding.encode(message.get("content", "")))
            total += 3  # Every message has overhead tokens

        total += 3  # Every conversation has overhead
        return total


# Global instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get or create global LLM client instance.

    Returns:
        LLMClient instance
    """
    global _llm_client

    if _llm_client is None:
        _llm_client = LLMClient()

    return _llm_client
