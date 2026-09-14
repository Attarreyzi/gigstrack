import React from 'react';

export default function Navbar({ liveCount = 0 }) {
  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <a href="/" className="brand-logo">
          <span className="dot-live"></span>
          <span>GIG<span style={{ color: 'var(--accent-pink)' }}>TRACK</span></span>
          <span className="brand-badge">RADAR</span>
        </a>

        <div className="nav-actions">
          {liveCount > 0 && (
            <div className="radar-live-tag" style={{ padding: '5px 14px', fontSize: '0.78rem' }}>
              <div className="radar-ping">
                <span></span>
                <span></span>
              </div>
              <span>{liveCount} Live Tonight</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
