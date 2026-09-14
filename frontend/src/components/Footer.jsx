import React from 'react';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <p style={{ marginBottom: '8px', fontWeight: 600, color: 'var(--text-secondary)' }}>
          🎸 GigTrack — Direktori & Radar Konser Musik Live Indonesia
        </p>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Dibuat dengan Python (Django REST Framework) & React.js. Pantau jadwal konser di kotamu setiap hari!
        </p>
      </div>
    </footer>
  );
}
