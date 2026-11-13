import { useEffect, useRef } from "react";

import type { DisplayMessage } from "../types/chat";

interface Props {
  messages: DisplayMessage[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: Props) {
  const endRef = useRef<HTMLDivElement>(null);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isLoading]);

  return (
    <div className="messages active">
      {messages.map((message) => (
        <article className={`message ${message.role}`} key={message.id}>
          <div className="message-avatar">{message.role === "user" ? "YOU" : "PW"}</div>
          <div className="bubble">
            <p>{message.content}</p>
            {!!message.citations?.length && (
              <div className="citations">
                <span>Sources</span>
                {message.citations.map((citation) => (
                  <a className="citation" href={citation.url} target="_blank" rel="noopener noreferrer" key={citation.url}>{citation.title}</a>
                ))}
              </div>
            )}
            {message.disclaimer && <div className="disclaimer">{message.disclaimer}</div>}
            {message.mode && <div className="mode-label">Answer mode: {message.mode}</div>}
          </div>
        </article>
      ))}
      {isLoading && (
        <article className="message assistant">
          <div className="message-avatar">PW</div>
          <div className="bubble typing" aria-label="Assistant is typing"><i /><i /><i /></div>
        </article>
      )}
      <div ref={endRef} />
    </div>
  );
}

