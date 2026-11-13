import { useState } from "react";

import { ChatHeader } from "./components/ChatHeader";
import { Composer } from "./components/Composer";
import { KnowledgeSidebar } from "./components/KnowledgeSidebar";
import { MessageList } from "./components/MessageList";
import { WelcomePanel } from "./components/WelcomePanel";
import { useChat } from "./features/chat/useChat";

export function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { messages, isLoading, ask } = useChat();

  return (
    <div className="app-shell">
      <KnowledgeSidebar open={menuOpen} />
      <main className="chat-main">
        <ChatHeader menuOpen={menuOpen} onMenuToggle={() => setMenuOpen((value) => !value)} />
        <section className="conversation" aria-live="polite">
          {messages.length === 0 && !isLoading
            ? <WelcomePanel onAsk={ask} />
            : <MessageList messages={messages} isLoading={isLoading} />}
        </section>
        <Composer disabled={isLoading} onAsk={ask} />
      </main>
      <button className={`mobile-overlay ${menuOpen ? "open" : ""}`} type="button" aria-label="Close knowledge panel" onClick={() => setMenuOpen(false)} />
    </div>
  );
}

