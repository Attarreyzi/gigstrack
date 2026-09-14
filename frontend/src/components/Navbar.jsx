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
            <div className="radar-live-tag" style={{ padding: '4px 12px', fontSize: '0.75rem' }}>
              <div className="radar-ping">
                <span></span>
                <span></span>
              </div>
              <span>{liveCount} Gig Hari Ini</span>
            </div>
          )}
          <a
            href="http://127.0.0.1:8000/admin/"
            target="_blank"
            rel="noreferrer"
            className="btn-admin-link"
            title="Buka Django Admin untuk tambah/edit data"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 20h9"></path>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
            <span>+ Admin Portal</span>
          </a>
        </div>
      </div>
    </header>
  );
}
