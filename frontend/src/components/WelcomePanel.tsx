const suggestions = [
  ["Explore treatment costs", "Published prices and context", "How much does alternative cancer treatment cost at ITC in Tijuana?"],
  ["Review package details", "Inclusions from the source page", "What is included in the adenocarcinoma treatment package?"],
  ["Learn about the clinic", "Location and clinic information", "Where is ITC Immunity Therapy Center located?"],
  ["Compare listed costs", "Only where both values exist", "Compare the alternative medicine costs listed on PlacidWay."],
] as const;

interface Props {
  onAsk(question: string): void;
}

export function WelcomePanel({ onAsk }: Props) {
  return (
    <div className="welcome">
      <div className="welcome-symbol" aria-hidden="true">
        <svg viewBox="0 0 48 48"><path d="M24 6c-5 0-9 4-9 9v4h-4c-5 0-9 4-9 9s4 9 9 9h4v4c0 5 4 9 9 9s9-4 9-9v-4h4c5 0 9-4 9-9s-4-9-9-9h-4v-4c0-5-4-9-9-9Z" /></svg>
      </div>
      <span className="eyebrow">PlacidWay website guide</span>
      <h1>What would you like to know?</h1>
      <p>Ask about ITC treatment packages, clinic information, or published costs. Answers come only from the approved PlacidWay pages.</p>
      <div className="suggestion-grid">
        {suggestions.map(([title, description, question]) => (
          <button className="suggestion" type="button" key={title} onClick={() => onAsk(question)}>
            <span className="suggestion-arrow">↗</span><strong>{title}</strong><small>{description}</small>
          </button>
        ))}
      </div>
    </div>
  );
}

