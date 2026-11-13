import { describe, expect, it } from "vitest";

import { buildChatPayload } from "../src/services/api/chatApi";
import { formatKnowledgeStatus } from "../src/services/api/knowledgeApi";

describe("chat API boundary", () => {
  it("keeps only the last twenty messages", () => {
    const messages = Array.from({ length: 25 }, (_, index) => ({
      role: (index % 2 ? "assistant" : "user") as "user" | "assistant",
      content: `message-${index}`,
    }));
    const payload = buildChatPayload(messages);
    expect(payload.messages).toHaveLength(20);
    expect(payload.messages[0].content).toBe("message-5");
  });

  it("describes unavailable knowledge without throwing", () => {
    expect(formatKnowledgeStatus({ status: "degraded" })).toBe("Knowledge status unavailable");
  });
});

