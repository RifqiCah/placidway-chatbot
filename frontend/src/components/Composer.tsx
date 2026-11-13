import { FormEvent, KeyboardEvent, useState } from "react";

interface Props {
  disabled: boolean;
  onAsk(question: string): void;
}

export function Composer({ disabled, onAsk }: Props) {
  const [question, setQuestion] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim() || disabled) return;
    onAsk(question);
    setQuestion("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  }

  return (
    <footer className="composer-wrap">
      <form className="composer" onSubmit={submit}>
        <label className="sr-only" htmlFor="message-input">Ask a question</label>
        <textarea
          id="message-input"
          rows={1}
          maxLength={4000}
          placeholder="Ask about treatments, packages, clinics, or costs…"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          onKeyDown={handleKeyDown}
          required
        />
        <button className="send-button" type="submit" aria-label="Send message" disabled={disabled}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 14-7-4 14-3-6-7-1Z" /></svg>
        </button>
      </form>
      <p className="composer-note"><span>ⓘ</span> Information is sourced from PlacidWay pages and is not a substitute for professional medical advice.</p>
    </footer>
  );
}

