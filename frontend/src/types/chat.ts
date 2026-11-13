export type ChatRole = "user" | "assistant";
export type AnswerStatus = "answered" | "unknown" | "medical_safety" | "action_unsupported" | "out_of_scope";
export type AnswerMode = "llm" | "extractive";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface Citation {
  title: string;
  url: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  status: AnswerStatus;
  mode: AnswerMode;
  disclaimer: string | null;
}

export interface DisplayMessage extends ChatMessage {
  id: string;
  citations?: Citation[];
  disclaimer?: string | null;
  mode?: AnswerMode;
}

