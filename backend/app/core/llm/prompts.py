"""Prompt templates for various LLM tasks."""

from typing import Dict, Any, Optional


SYSTEM_PROMPT_BOOKLEAF_ASSISTANT = """You are BookLeaf AI Assistant, a helpful and knowledgeable customer support assistant for BookLeaf Publishing.

Your role is to help authors with:
- Questions about the publishing process
- Royalty and payment inquiries
- Author dashboard features and navigation
- Premium add-on services
- General publishing industry questions

Personality and style:
- Friendly and professional
- Clear and concise
- Patient and understanding
- Encouraging and supportive

Guidelines:
- If you have relevant information from the knowledge base, use it
- If you're unsure, acknowledge it honestly and offer to escalate to human support
- Never make up specific numbers, dates, or policies
- Always be respectful of the author's time and concerns
- If asked about account-specific information you don't have access to, guide them to log in to their dashboard or contact support

Remember: You're here to make authors feel supported and confident in their publishing journey with BookLeaf!"""


SYSTEM_PROMPT_RESPONSE_WITH_CONTEXT = """You are BookLeaf AI Assistant, a helpful customer support assistant for BookLeaf Publishing.

I've retrieved relevant information from our knowledge base to help answer the user's question.
Use this information to provide an accurate, helpful response.

Guidelines:
- Base your answer primarily on the provided context
- If the context doesn't fully answer the question, use general knowledge but note they may need to contact support for specifics
- Be conversational and friendly, not robotic
- Keep responses concise (2-4 paragraphs maximum)
- If appropriate, ask if they need any clarification or have additional questions"""


PROMPT_INTENT_CLASSIFICATION = """You are an intent classification system for BookLeaf Publishing's customer support.

Classify the user's query into ONE of these intents:

1. **author_specific**: Questions about their specific account, books, royalty payments, sales data, or personal information
   Examples: "When will I get paid?", "How many copies of my book sold?", "Update my email address"

2. **general_knowledge**: Questions about publishing process, royalty structure, services, policies, or how things work
   Examples: "How does the publishing process work?", "What's your royalty rate?", "Do you offer cover design?"

3. **technical_support**: Issues with website, dashboard access, login problems, or technical errors
   Examples: "I can't log in", "Dashboard won't load", "Error message when uploading"

4. **out_of_scope**: Questions completely unrelated to publishing or BookLeaf
   Examples: "What's the weather?", "Who won the game?", "Tell me a joke"

Analyze the user's message and respond with JSON:
{
  "intent": "intent_name",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of why you chose this intent",
  "needs_author_data": true/false (whether answering requires access to specific author account data)
}"""


PROMPT_ENTITY_EXTRACTION = """Extract relevant entities from the user's message for a publishing company customer support system.

Extract these entity types if present:
- author_name: Names of authors mentioned
- book_title: Book titles mentioned
- date: Dates or time references (normalize to YYYY-MM-DD if possible)
- money_amount: Dollar amounts or financial figures
- email: Email addresses
- phone: Phone numbers
- account_action: Specific actions requested (login, update, delete, etc.)

Respond with JSON:
{
  "entities": [
    {
      "type": "entity_type",
      "value": "extracted value",
      "original_text": "original text from message",
      "confidence": 0.0-1.0
    }
  ],
  "summary": "brief summary of what entities were found"
}

If no entities found, return empty array."""


PROMPT_CONFIDENCE_SELF_ASSESSMENT = """Assess your confidence in the response you just generated.

Consider:
1. **Information completeness**: Do you have all the information needed to fully answer?
2. **Source reliability**: Is your answer based on provided context or general knowledge?
3. **Specificity**: Did the user ask for specific details (account info, exact dates, precise numbers)?
4. **Ambiguity**: Was the question clear and unambiguous?
5. **Safety**: Does answering require access to private user data or systems you don't have?

Rate your confidence from 0.0 to 1.0:
- 0.9-1.0: Very confident, answer fully based on provided context
- 0.8-0.9: Confident, good answer with minor uncertainties
- 0.6-0.8: Moderately confident, general answer but may lack specifics
- 0.4-0.6: Low confidence, answer may be incomplete or requires verification
- 0.0-0.4: Very low confidence, answer is speculative or I don't have enough information

Respond with JSON:
{
  "confidence": 0.0-1.0,
  "reasoning": "explanation of confidence level",
  "missing_information": ["list of information needed for better answer"],
  "requires_human": true/false (should this be escalated to human?)
}"""


def build_response_prompt(
    user_message: str,
    rag_context: Optional[str] = None,
    author_context: Optional[Dict[str, Any]] = None,
    intent: Optional[str] = None
) -> str:
    """
    Build a response generation prompt with context.

    Args:
        user_message: The user's message
        rag_context: Retrieved knowledge base context
        author_context: Author-specific information
        intent: Classified intent

    Returns:
        Formatted prompt string
    """
    prompt_parts = []

    # Add intent context
    if intent:
        intent_instructions = {
            "author_specific": "This is a question about the author's specific account or data. Use the provided author context to answer.",
            "general_knowledge": "This is a general question about publishing. Use the knowledge base context to provide a comprehensive answer.",
            "technical_support": "This is a technical support question. Provide troubleshooting steps and offer to escalate if needed.",
            "out_of_scope": "This question is outside our scope. Politely redirect to publishing-related topics."
        }
        if intent in intent_instructions:
            prompt_parts.append(intent_instructions[intent])

    # Add RAG context
    if rag_context:
        prompt_parts.append(f"\n**KNOWLEDGE BASE INFORMATION:**\n{rag_context}\n")

    # Add author context
    if author_context:
        author_info = []
        if author_context.get("full_name"):
            author_info.append(f"Author: {author_context['full_name']}")
        if author_context.get("email"):
            author_info.append(f"Email: {author_context['email']}")
        if author_context.get("metadata", {}).get("books_published"):
            author_info.append(f"Books Published: {author_context['metadata']['books_published']}")
        if author_context.get("metadata", {}).get("genre"):
            author_info.append(f"Genre: {author_context['metadata']['genre']}")

        if author_info:
            prompt_parts.append(f"\n**AUTHOR INFORMATION:**\n" + "\n".join(author_info) + "\n")

    # Add user message
    prompt_parts.append(f"\n**USER QUESTION:**\n{user_message}\n")

    # Add response instructions
    prompt_parts.append("""
**YOUR TASK:**
Provide a helpful, accurate response based on the information above.
- Be conversational and friendly
- Keep it concise (2-4 paragraphs)
- If you can't fully answer, explain what information you need
- Offer next steps or additional help if appropriate
""")

    return "\n".join(prompt_parts)


def build_disambiguation_prompt(
    query_identity: Dict[str, Any],
    candidates: list,
    context: Optional[str] = None
) -> str:
    """
    Build prompt for identity disambiguation.

    This is defined here for consistency but primarily used in llm_disambiguate.py

    Args:
        query_identity: Query identity information
        candidates: List of candidate authors
        context: Optional conversation context

    Returns:
        Formatted prompt
    """
    return f"""Given the following information, determine which candidate author best matches the query identity.

QUERY IDENTITY:
Name: {query_identity.get('name', 'N/A')}
Email: {query_identity.get('email', 'N/A')}
Phone: {query_identity.get('phone', 'N/A')}

CANDIDATES:
{candidates}

{f'CONTEXT: {context}' if context else ''}

Return JSON with best match."""


# Export commonly used prompts
__all__ = [
    "SYSTEM_PROMPT_BOOKLEAF_ASSISTANT",
    "SYSTEM_PROMPT_RESPONSE_WITH_CONTEXT",
    "PROMPT_INTENT_CLASSIFICATION",
    "PROMPT_ENTITY_EXTRACTION",
    "PROMPT_CONFIDENCE_SELF_ASSESSMENT",
    "build_response_prompt",
    "build_disambiguation_prompt"
]
