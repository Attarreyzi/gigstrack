import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar({
  liveCount = 0,
  activeTab = 'gigs',
  setActiveTab,
  onNavigate,
  onOpenAuth,
  onToggleSearch,
  isSearchVisible = false,
}) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();

  // Close drawer on ESC key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setDrawerOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    if (drawerOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [drawerOpen]);

  const handleMenuClick = (itemKey) => {
    setDrawerOpen(false);
    if (onNavigate) {
      onNavigate(itemKey);
    } else if (setActiveTab) {
      if (itemKey === 'today') {
        setActiveTab('gigs');
      } else {
        setActiveTab(itemKey);
      }
    }
  };

  return (
    <>
      <header className="navbar">
        <div className="container navbar-inner">
          {/* Sisi Kiri: Logo Brand */}
          <div className="nav-brand-col">
            <a
              href="/"
              className="brand-logo"
              onClick={(e) => {
                e.preventDefault();
                handleMenuClick('gigs');
              }}
            >
              <span className="dot-live"></span>
              <span>GIGS<span style={{ color: 'var(--accent-pink)' }}>TRACK</span></span>
              <span className="brand-badge">RADAR</span>
            </a>
          </div>

          {/* Sisi Tengah: Menu Desktop Terpusat Simetris (Persis Gambar Hai-Grid) */}
          <nav className="desktop-nav-links" aria-label="Main Navigation">
            <button
              type="button"
              className={`desktop-nav-link ${activeTab === 'gigs' ? 'active' : ''}`}
              onClick={() => handleMenuClick('gigs')}
            >
              Jadwal Konser
            </button>
            <button
              type="button"
              className={`desktop-nav-link ${activeTab === 'today' ? 'active' : ''}`}
              onClick={() => handleMenuClick('today')}
            >
              Gigs Hari Ini
              {liveCount > 0 && <span className="nav-badge-pill">{liveCount} LIVE</span>}
            </button>
            <button
              type="button"
              className={`desktop-nav-link ${activeTab === 'artists' ? 'active' : ''}`}
              onClick={() => handleMenuClick('artists')}
            >
              Katalog Band
            </button>
            <button
              type="button"
              className={`desktop-nav-link ${activeTab === 'about' ? 'active' : ''}`}
              onClick={() => handleMenuClick('about')}
            >
              About Us
            </button>
            <button
              type="button"
              className={`desktop-nav-link ${activeTab === 'contact' ? 'active' : ''}`}
              onClick={() => handleMenuClick('contact')}
            >
              Contact Us
            </button>
          </nav>

          {/* Sisi Kanan: Aksi Search, User Chip, & Hamburger */}
          <div className="nav-actions">
            {/* Teleskop Search Icon Button (Toggle Search Bar di atas Dropdown Wilayah) */}
            <button
              type="button"
              className={`nav-search-trigger-btn ${isSearchVisible ? 'active' : ''}`}
              onClick={onToggleSearch}
              title={isSearchVisible ? 'Tutup Kolom Pencarian' : 'Cari Konser & Artis'}
              aria-label="Cari Konser"
            >
              <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </button>

            {liveCount > 0 && (
              <div
                className="radar-live-tag nav-radar-live-tag"
                style={{ cursor: 'pointer' }}
                onClick={() => handleMenuClick('today')}
                title="Lihat konser yang sedang aktif hari ini"
              >
                <div className="radar-ping">
                  <span></span>
                  <span></span>
                </div>
                <span className="live-tag-text">{liveCount} Live Tonight</span>
                <span className="live-tag-mobile-text">{liveCount} Live</span>
              </div>
            )}

            {isAuthenticated ? (
              <div className="nav-user-chip">
                <div className="nav-user-avatar">
                  <span>
                    {user?.first_name
                      ? user.first_name[0].toUpperCase()
                      : (user?.username ? user.username[0].toUpperCase() : 'U')}
                  </span>
                </div>
                <div className="nav-user-meta">
                  <span className="nav-user-name">
                    {user?.first_name || user?.username}
                  </span>
                  <span className="nav-user-provider">
                    {user?.auth_provider === 'google' ? 'Google' : user?.auth_provider === 'guest' ? 'Tamu' : 'Member'}
                  </span>
                </div>
                <button
                  type="button"
                  className="nav-logout-btn"
                  onClick={logout}
                  title="Keluar / Logout"
                  aria-label="Logout"
                >
                  ✕
                </button>
              </div>
            ) : (
              <button
                type="button"
                className="btn-primary nav-login-btn"
                onClick={onOpenAuth}
              >
                Login
              </button>
            )}

            {/* Hamburger Button (Hanya Muncul di Mobile) */}
            <button
              type="button"
              className="nav-hamburger-btn"
              onClick={() => setDrawerOpen(true)}
              aria-label="Buka Menu Navigasi"
              title="Menu Navigasi"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="4" y1="7" x2="20" y2="7"></line>
                <line x1="4" y1="12" x2="20" y2="12"></line>
                <line x1="4" y1="17" x2="20" y2="17"></line>
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Sidebar Drawer Navigation */}
      {drawerOpen && (
        <div className="drawer-backdrop" onClick={() => setDrawerOpen(false)}>
          <aside className="drawer-panel" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <div className="brand-logo" style={{ fontSize: '1.15rem' }}>
                <span className="dot-live"></span>
                <span>GIGS<span style={{ color: 'var(--accent-pink)' }}>TRACK</span></span>
              </div>
              <button
                type="button"
                className="drawer-close-btn"
                onClick={() => setDrawerOpen(false)}
                aria-label="Tutup Menu"
              >
                ✕
              </button>
            </div>

            {/* Mobile Drawer Account Card */}
            <div className="drawer-user-section">
              {isAuthenticated ? (
                <div className="drawer-user-card">
                  <div className="drawer-user-avatar">
                    <span>
                      {user?.first_name
                        ? user.first_name[0].toUpperCase()
                        : (user?.username ? user.username[0].toUpperCase() : 'U')}
                    </span>
                  </div>
                  <div className="drawer-user-info">
                    <span className="drawer-user-name">
                      {user?.first_name || user?.username}
                    </span>
                    <span className="drawer-user-role">
                      {user?.auth_provider === 'google' ? 'Akun Google' : user?.auth_provider === 'guest' ? 'Tamu' : 'Member'}
                    </span>
                  </div>
                  <button
                    type="button"
                    className="drawer-logout-btn"
                    onClick={() => {
                      logout();
                      setDrawerOpen(false);
                    }}
                    title="Keluar"
                  >
                    Keluar
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  className="btn-primary drawer-login-btn"
                  onClick={() => {
                    setDrawerOpen(false);
                    if (onOpenAuth) onOpenAuth();
                  }}
                >
                  Masuk / Hubungkan Google
                </button>
              )}
            </div>

            <nav className="drawer-nav">
              <button
                type="button"
                className="drawer-item"
                onClick={() => {
                  setDrawerOpen(false);
                  if (onToggleSearch) onToggleSearch();
                }}
              >
                <span className="drawer-item-title">🔍 Cari Konser & Artis</span>
              </button>

              <button
                type="button"
                className={`drawer-item ${activeTab === 'gigs' ? 'active' : ''}`}
                onClick={() => handleMenuClick('gigs')}
              >
                <span className="drawer-item-title">Jadwal Konser</span>
              </button>

              <button
                type="button"
                className="drawer-item"
                onClick={() => handleMenuClick('today')}
              >
                <span className="drawer-item-title">Gigs Hari Ini</span>
                {liveCount > 0 && <span className="drawer-badge-live">{liveCount} LIVE</span>}
              </button>

              <button
                type="button"
                className={`drawer-item ${activeTab === 'artists' ? 'active' : ''}`}
                onClick={() => handleMenuClick('artists')}
              >
                <span className="drawer-item-title">Katalog Band</span>
              </button>

              <button
                type="button"
                className={`drawer-item ${activeTab === 'saved' ? 'active' : ''}`}
                onClick={() => handleMenuClick('saved')}
              >
                <span className="drawer-item-title">Konser Tersimpan</span>
              </button>

              <button
                type="button"
                className={`drawer-item ${activeTab === 'about' ? 'active' : ''}`}
                onClick={() => handleMenuClick('about')}
              >
                <span className="drawer-item-title">About Us</span>
              </button>

              <button
                type="button"
                className={`drawer-item ${activeTab === 'contact' ? 'active' : ''}`}
                onClick={() => handleMenuClick('contact')}
              >
                <span className="drawer-item-title">Contact Us</span>
              </button>
            </nav>

            <div className="drawer-footer">
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                GigsTrack Radar Musik Independen & Festival
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                v2.1 - Jabodetabek & Live Radar
              </div>

              {/* Social Channels in Drawer Footer */}
              <div className="drawer-social-links">
                <a
                  href="https://instagram.com"
                  target="_blank"
                  rel="noreferrer"
                  className="drawer-social-btn"
                  title="Instagram @gigstrack.id"
                  aria-label="Instagram"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
                    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
                    <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
                  </svg>
                </a>
                <a
                  href="https://wa.me/6281234567890"
                  target="_blank"
                  rel="noreferrer"
                  className="drawer-social-btn"
                  title="WhatsApp Admin"
                  aria-label="WhatsApp"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
                  </svg>
                </a>
                <a
                  href="mailto:halo@gigtrack.id"
                  className="drawer-social-btn"
                  title="Email halo@gigtrack.id"
                  aria-label="Email"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                    <polyline points="22,6 12,13 2,6" />
                  </svg>
                </a>
              </div>
            </div>
          </aside>
        </div>
      )}
    </>
  );
}
