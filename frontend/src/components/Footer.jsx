import React from 'react';

export default function Footer({ onNavigate }) {
  const handleNav = (target) => {
    if (onNavigate) {
      onNavigate(target);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="hai-footer">
      <div className="hai-footer-container">
        {/* ===================================================
            1. DESKTOP VIEW (>= 768px) - 3-Column Horizontal (Gambar 2 Hai)
            =================================================== */}
        <div className="hai-footer-desktop-view">
          <div className="hai-footer-main">
            {/* Kolom 1: Logo Brand */}
            <div className="hai-footer-brand-col">
              <button
                type="button"
                className="hai-footer-logo-btn"
                onClick={() => handleNav('gigs')}
                title="GigsTrack Home"
              >
                <span className="hai-footer-logo-text">GigsTrack</span>
                <span className="hai-footer-logo-sub">LIVE RADAR</span>
              </button>
            </div>

            {/* Kolom 2: Vertical Navigation Links */}
            <nav className="hai-footer-nav-col" aria-label="Footer Navigation Desktop">
              <button
                type="button"
                className="hai-footer-nav-link"
                onClick={() => handleNav('about')}
              >
                About us
              </button>
              <button
                type="button"
                className="hai-footer-nav-link"
                onClick={() => handleNav('contact')}
              >
                Contact us
              </button>
              <button
                type="button"
                className="hai-footer-nav-link"
                onClick={() => handleNav('gigs')}
              >
                Radar Konser
              </button>
            </nav>

            {/* Kolom 3: Kota Liputan Radar Gigs */}
            <div className="hai-footer-network-col">
              <div className="hai-network-header">
                <span className="hai-network-tagline">LOKASI RADAR GIGS</span>
              </div>

              <div className="hai-network-partners">
                <span>Jakarta</span>
                <span className="hai-pipe">|</span>
                <span>Bogor</span>
                <span className="hai-pipe">|</span>
                <span>Bandung</span>
                <span className="hai-pipe">|</span>
                <span>Tangerang</span>
                <span className="hai-pipe">|</span>
                <span>Bekasi</span>
              </div>
            </div>
          </div>

          <div className="hai-footer-divider"></div>

          <div className="hai-footer-bottom">
            <p className="hai-footer-copyright">Hak Cipta © GigsTrack 2026</p>
          </div>
        </div>

        {/* ===================================================
            2. MOBILE VIEW (< 768px) - Centered Stack (Gambar 1 Mobile Hai)
            =================================================== */}
        <div className="hai-footer-mobile-view">
          {/* Logo / Hub Brand */}
          <div className="hai-mobile-hub-brand">
            <span className="hai-mobile-hub-title">GIGSTRACK</span>
            <span className="hai-mobile-hub-sub">LIVE RADAR HUB</span>
          </div>

          {/* Socials: find us on */}
          <div className="hai-mobile-socials-section">
            <span className="hai-mobile-find-us">find us on:</span>
            <div className="hai-mobile-accent-bar"></div>
            <div className="hai-mobile-social-icons">
              <a
                href="https://instagram.com/gigstrack"
                target="_blank"
                rel="noreferrer"
                className="hai-social-circle-btn"
                title="Instagram"
                aria-label="Instagram"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                  <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                  <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
                </svg>
              </a>
              <a
                href="https://wa.me/6281234567890"
                target="_blank"
                rel="noreferrer"
                className="hai-social-circle-btn"
                title="WhatsApp"
                aria-label="WhatsApp"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                </svg>
              </a>
              <a
                href="mailto:halo@gigtrack.id"
                className="hai-social-circle-btn"
                title="Email Redaksi"
                aria-label="Email"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="4" width="20" height="16" rx="2"></rect>
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
                </svg>
              </a>
            </div>
          </div>

          {/* Kota Jaringan Radar (Rata Tengah) */}
          <div className="hai-mobile-cities-row">
            <span>Jakarta</span>
            <span className="hai-pipe">|</span>
            <span>Bogor</span>
            <span className="hai-pipe">|</span>
            <span>Bandung</span>
            <span className="hai-pipe">|</span>
            <span>Tangerang</span>
            <span className="hai-pipe">|</span>
            <span>Bekasi</span>
          </div>

          <div className="hai-footer-divider"></div>

          {/* Navigasi Horizontal dengan Bullet (Sesuai Gambar 1 Mobile) */}
          <nav className="hai-mobile-nav-row" aria-label="Footer Navigation Mobile">
            <button
              type="button"
              className="hai-mobile-nav-link"
              onClick={() => handleNav('about')}
            >
              About us
            </button>
            <span className="hai-bullet">•</span>
            <button
              type="button"
              className="hai-mobile-nav-link"
              onClick={() => handleNav('contact')}
            >
              Contact us
            </button>
            <span className="hai-bullet">•</span>
            <button
              type="button"
              className="hai-mobile-nav-link"
              onClick={() => handleNav('gigs')}
            >
              Radar Konser
            </button>
          </nav>

          {/* Hak Cipta Tengah (Sesuai Gambar 1 Mobile) */}
          <p className="hai-mobile-copyright">Hak Cipta © GigsTrack 2026</p>
        </div>
      </div>
    </footer>
  );
}
