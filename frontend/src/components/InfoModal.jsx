import React, { useEffect } from 'react';

export default function InfoModal({ isOpen, onClose, initialTab = 'about' }) {
  const [activeTab, setActiveTab] = React.useState(initialTab);

  useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab]);

  useEffect(() => {
    if (isOpen) {
      const handleKeyDown = (e) => {
        if (e.key === 'Escape') onClose();
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose} style={{ zIndex: 1100 }}>
      <div
        className="modal-content info-modal-content"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '580px', padding: 0, overflow: 'hidden' }}
      >
        {/* Header with Close */}
        <div className="info-modal-header">
          <div className="info-modal-brand">
            <span className="dot-live"></span>
            <span>GIGS<span style={{ color: 'var(--accent-pink)' }}>TRACK</span></span>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Tutup"
            style={{ position: 'static' }}
          >
            ✕
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="info-tab-switcher">
          <button
            type="button"
            className={`info-tab-btn ${activeTab === 'about' ? 'active' : ''}`}
            onClick={() => setActiveTab('about')}
          >
            Tentang GigsTrack
          </button>
          <button
            type="button"
            className={`info-tab-btn ${activeTab === 'contact' ? 'active' : ''}`}
            onClick={() => setActiveTab('contact')}
          >
            Hubungi Kami & Kerjasama
          </button>
        </div>

        {/* Modal Body */}
        <div className="info-modal-body">
          {activeTab === 'about' ? (
            <div className="info-section-fade">
              <div className="info-hero-badge">
                RADAR MUSIK LIVE INDEPENDEN JABODETABEK
              </div>
              <h3 className="info-title">
                Menghubungkan Panggung, Musisi, & Penonton Sejati.
              </h3>
              <p className="info-paragraph">
                <strong>GigsTrack</strong> lahir dari kecintaan pada kultur panggung musik live. Kami adalah platform radar terkurasi yang memantau denyut jadwal gigs indie, showcase musisi lokal, hingga agenda festival musik besar di Jakarta, Bogor, Depok, Tangerang, dan Bekasi.
              </p>

              <div className="info-features-grid">
                <div className="info-feature-card">
                  <div className="info-feature-icon">📡</div>
                  <div className="info-feature-title">Live Tonight Radar</div>
                  <div className="info-feature-desc">
                    Pantau gigs yang berlangsung hari ini secara real-time lengkap dengan rute lokasi venue.
                  </div>
                </div>

                <div className="info-feature-card">
                  <div className="info-feature-icon">🤖</div>
                  <div className="info-feature-title">AI Poster Scanner</div>
                  <div className="info-feature-desc">
                    Cukup kirim foto poster flyer konser lewat bot Telegram, AI otomatis mengekstrak jadwal, harga tiket, dan susunan band.
                  </div>
                </div>

                <div className="info-feature-card">
                  <div className="info-feature-icon">🎸</div>
                  <div className="info-feature-title">Lineup & Multi-Day</div>
                  <div className="info-feature-desc">
                    Navigasi festival musik harian (Day 1, Day 2, Day 3) yang rapi tanpa perlu pusing mencari rundown.
                  </div>
                </div>

                <div className="info-feature-card">
                  <div className="info-feature-icon">🎟️</div>
                  <div className="info-feature-title">Platform Tiket Resmi</div>
                  <div className="info-feature-desc">
                    Akses langsung ke penyedia tiket resmi terpercaya serta penandaan event gratis (Free Entry).
                  </div>
                </div>
              </div>

              <div className="info-quote-box">
                "Musik live bukan sekadar tontonan, tapi ruang perjumpaan dan energi kolektif."
              </div>
            </div>
          ) : (
            <div className="info-section-fade">
              <div className="info-hero-badge" style={{ color: 'var(--accent-cyan)', borderColor: 'rgba(0, 240, 255, 0.4)', background: 'rgba(0, 240, 255, 0.1)' }}>
                KERJASAMA, SUBMIT GIGS & MEDIA PARTNER
              </div>
              <h3 className="info-title">
                Mari Bergerak Bersama Memajukan Panggung Musik.
              </h3>
              <p className="info-paragraph">
                Apakah Anda seorang <strong>musisi</strong>, <strong>kolektif</strong>, <strong>promotor festival</strong>, atau <strong>pemilik venue</strong>? Kami membuka pintu kolaborasi seluas-luasnya untuk mempublikasikan acara Anda ke ribuan penikmat musik aktif.
              </p>

              <div className="contact-cards-list">
                <a
                  href="https://t.me"
                  target="_blank"
                  rel="noreferrer"
                  className="contact-card-item"
                >
                  <div className="contact-card-icon" style={{ background: 'rgba(0, 136, 204, 0.2)', color: '#0088cc' }}>
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="22" y1="2" x2="11" y2="13" />
                      <polygon points="22 2 15 22 11 13 2 9 22 2" />
                    </svg>
                  </div>
                  <div className="contact-card-content">
                    <div className="contact-card-label">Submit Poster via Telegram Bot</div>
                    <div className="contact-card-value">@GigTrackBot (Scan Otomatis AI)</div>
                    <div className="contact-card-sub">Kirim foto poster konser untuk langsung terbit di radar</div>
                  </div>
                </a>

                <a
                  href="https://instagram.com"
                  target="_blank"
                  rel="noreferrer"
                  className="contact-card-item"
                >
                  <div className="contact-card-icon" style={{ background: 'rgba(255, 0, 85, 0.2)', color: 'var(--accent-pink)' }}>
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
                      <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
                      <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
                    </svg>
                  </div>
                  <div className="contact-card-content">
                    <div className="contact-card-label">Instagram & Media Partner</div>
                    <div className="contact-card-value">@gigtrack.id</div>
                    <div className="contact-card-sub">DM kami untuk liputan gigs, rilis pers, & kerja sama media</div>
                  </div>
                </a>

                <a
                  href="mailto:halo@gigtrack.id"
                  className="contact-card-item"
                >
                  <div className="contact-card-icon" style={{ background: 'rgba(0, 240, 255, 0.2)', color: 'var(--accent-cyan)' }}>
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                      <polyline points="22,6 12,13 2,6" />
                    </svg>
                  </div>
                  <div className="contact-card-content">
                    <div className="contact-card-label">Email Partnership & Sponsorship</div>
                    <div className="contact-card-value">partnership@gigtrack.id</div>
                    <div className="contact-card-sub">Proposal festival, brand activation, & integrasi tiket</div>
                  </div>
                </a>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="info-modal-footer">
          <span>GigsTrack &copy; 2026 • Kurasi Radar Musik Independen</span>
          <button type="button" className="btn-secondary" onClick={onClose} style={{ padding: '6px 16px', fontSize: '0.8rem' }}>
            Tutup
          </button>
        </div>
      </div>
    </div>
  );
}
