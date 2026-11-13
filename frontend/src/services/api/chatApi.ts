import type { ChatMessage, ChatResponse } from "../../types/chat";

export function buildChatPayload(messages: ChatMessage[]): { messages: ChatMessage[] } {
  return { messages: messages.slice(-20) };
}

export async function sendChat(messages: ChatMessage[]): Promise<ChatResponse> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(buildChatPayload(messages)),
  });
  if (!response.ok) {
    throw new Error(`Chat request failed (${response.status})`);
  }
  return response.json() as Promise<ChatResponse>;
}

