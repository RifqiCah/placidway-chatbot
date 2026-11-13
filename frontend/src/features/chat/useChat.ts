import { useCallback, useState } from "react";

import { sendChat } from "../../services/api/chatApi";
import type { ChatMessage, DisplayMessage } from "../../types/chat";

function messageId(): string {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
}

export function useChat() {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const ask = useCallback(async (question: string) => {
    const content = question.trim();
    if (!content || isLoading) return;
    const userMessage: DisplayMessage = { id: messageId(), role: "user", content };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setIsLoading(true);
    try {
      const history: ChatMessage[] = nextMessages.map(({ role, content: text }) => ({ role, content: text }));
      const response = await sendChat(history);
      setMessages((current) => [
        ...current,
        {
          id: messageId(),
          role: "assistant",
          content: response.answer,
          citations: response.citations,
          disclaimer: response.disclaimer,
          mode: response.mode,
        },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: messageId(),
          role: "assistant",
          content: "I couldn't reach the knowledge service. Please try again in a moment.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, messages]);

  return { messages, isLoading, ask };
}

