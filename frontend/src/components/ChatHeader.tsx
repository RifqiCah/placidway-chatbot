interface Props {
  menuOpen: boolean;
  onMenuToggle(): void;
}

export function ChatHeader({ menuOpen, onMenuToggle }: Props) {
  return (
    <header className="topbar">
      <button className="menu-button" type="button" aria-label="Open knowledge panel" aria-expanded={menuOpen} onClick={onMenuToggle}>
        <span /><span /><span />
      </button>
      <div className="assistant-identity">
        <div className="assistant-avatar"><span>PW</span><i /></div>
        <div><strong>Medical Travel Assistant</strong><small><span className="online-dot" /> Online · Website knowledge only</small></div>
      </div>
      <span className="privacy-pill">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 10V7a5 5 0 0 1 10 0v3m-11 0h12v10H6V10Z" /></svg>
        Private conversation
      </span>
    </header>
  );
}

