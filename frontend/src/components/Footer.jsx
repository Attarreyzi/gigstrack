import React from 'react';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <p style={{ marginBottom: '8px', fontWeight: 600, color: 'var(--text-secondary)' }}>
          GigTrack — Direktori & Radar Konser Musik Live Indonesia
        </p>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Dibuat dengan Python (Django REST Framework) & React.js. Pantau jadwal konser di kotamu setiap hari.
        </p>
        <div>
          <a
            href="http://127.0.0.1:8000/admin/"
            target="_blank"
            rel="noreferrer"
            style={{
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              textDecoration: 'underline',
              opacity: 0.6,
              transition: 'opacity 0.2s'
            }}
            onMouseOver={(e) => (e.currentTarget.style.opacity = '1')}
            onMouseOut={(e) => (e.currentTarget.style.opacity = '0.6')}
          >
            Organizer & Admin Portal Access
          </a>
        </div>
      </div>
    </footer>
  );
}
