import React, { useEffect } from 'react';

// ========================================================
// PENGATURAN KONTAK GIGSTRACK
// ========================================================
const CONTACT_DATA = {
  email: {
    address: 'halo@gigtrack.id',
    link: 'mailto:halo@gigtrack.id',
    label: 'Kirim Email ke Redaksi & Info Kerjasama',
  },
  whatsapp: {
    number: '+62 812-3456-7890',
    link: 'https://wa.me/6281234567890',
    label: 'Chat Hotline Admin Kurasi & Submit Flyer',
  },
  instagram: {
    handle: '@gigstrack',
    link: 'https://instagram.com/gigstrack',
    label: 'Akun Instagram Resmi Radar Gigs',
  },
};

export default function ContactPage({ onNavigate }) {
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  return (
    <div className="hai-editorial-page">
      <div className="hai-editorial-container">
        {/* Navigasi Kembali */}
        <div className="hai-editorial-nav">
          <button
            type="button"
            className="hai-editorial-back-btn"
            onClick={() => onNavigate && onNavigate('gigs')}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            <span>KEMBALI KE RADAR KONSER</span>
          </button>
        </div>

        {/* Judul Artikel Editorial */}
        <h1 className="hai-editorial-title">Contact us</h1>

        {/* Lead Narasi Hubungi Kami - Ringkas & Padat */}
        <p className="hai-editorial-paragraph">
          Punya pertanyaan seputar kurasi konser, kerja sama festival, atau ingin kirim flyer bandmu? Hubungi kami langsung melalui saluran resmi di bawah ini:
        </p>

        {/* 3 Direct Channels - Interaktif & Ramah Layar HP */}
        <div className="hai-editorial-contact-grid">
          {/* Channel 1: Email */}
          <a
            href={CONTACT_DATA.email.link}
            className="hai-contact-tile tile-email"
            title="Kirim Email ke Redaksi"
          >
            <div className="hai-tile-icon email-bg">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="4" width="20" height="16" rx="2"></rect>
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
              </svg>
            </div>
            <div className="hai-tile-body">
              <span className="hai-tile-tag">EMAIL REDAKSI</span>
              <strong className="hai-tile-title">{CONTACT_DATA.email.address}</strong>
              <span className="hai-tile-sub">{CONTACT_DATA.email.label}</span>
            </div>
            <span className="hai-tile-action">Kirim Email ↗</span>
          </a>

          {/* Channel 2: WhatsApp */}
          <a
            href={CONTACT_DATA.whatsapp.link}
            target="_blank"
            rel="noopener noreferrer"
            className="hai-contact-tile tile-wa"
            title="Chat Hotline WhatsApp"
          >
            <div className="hai-tile-icon wa-bg">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
              </svg>
            </div>
            <div className="hai-tile-body">
              <span className="hai-tile-tag">HOTLINE WHATSAPP</span>
              <strong className="hai-tile-title">{CONTACT_DATA.whatsapp.number}</strong>
              <span className="hai-tile-sub">{CONTACT_DATA.whatsapp.label}</span>
            </div>
            <span className="hai-tile-action">Buka Chat ↗</span>
          </a>

          {/* Channel 3: Instagram */}
          <a
            href={CONTACT_DATA.instagram.link}
            target="_blank"
            rel="noopener noreferrer"
            className="hai-contact-tile tile-ig"
            title="Kunjungi Instagram Resmi"
          >
            <div className="hai-tile-icon ig-bg">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
              </svg>
            </div>
            <div className="hai-tile-body">
              <span className="hai-tile-tag">INSTAGRAM OFFICIAL</span>
              <strong className="hai-tile-title">{CONTACT_DATA.instagram.handle}</strong>
              <span className="hai-tile-sub">{CONTACT_DATA.instagram.label}</span>
            </div>
            <span className="hai-tile-action">Follow IG ↗</span>
          </a>
        </div>

        {/* Tombol Aksi Editorial */}
        <div className="hai-editorial-actions" style={{ marginTop: '36px' }}>
          <button
            type="button"
            className="hai-editorial-btn-primary"
            onClick={() => onNavigate && onNavigate('gigs')}
          >
            Kembali ke Radar Konser
          </button>
          <button
            type="button"
            className="hai-editorial-btn-secondary"
            onClick={() => onNavigate && onNavigate('about')}
          >
            Tentang GigsTrack (About Us)
          </button>
        </div>
      </div>
    </div>
  );
}
