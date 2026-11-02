import React, { useEffect } from 'react';

export default function AboutPage({ onNavigate }) {
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
        <h1 className="hai-editorial-title">About us</h1>

        {/* Isi Narasi Editorial - Ringkas, Padat, & Bebas Wall of Text */}
        <article className="hai-editorial-article">
          <p className="hai-editorial-paragraph">
            <strong>GigsTrack</strong> beroperasi sebagai basis data dan radar panduan konser musik di Indonesia. Menghadirkan arsip dan kurasi jadwal panggung musisi, festival lintas kota, direktori ruang pertunjukan, serta akses kanal transaksi tiket terverifikasi. <em>Live music always needs a dedicated space to celebrate together.</em>
          </p>

          {/* 3 Pilar Layanan Radar - Terstruktur & Nyaman di Layar HP */}
          <div className="hai-editorial-pillars">
            <div className="hai-pillar-card">
              <span className="hai-pillar-num">01</span>
              <div className="hai-pillar-info">
                <strong className="hai-pillar-title">Live Tonight Radar</strong>
                <p className="hai-pillar-desc">
                  Pantau panggung musik yang aktif hari ini lengkap dengan info venue dan jam gate open.
                </p>
              </div>
            </div>

            <div className="hai-pillar-card">
              <span className="hai-pillar-num">02</span>
              <div className="hai-pillar-info">
                <strong className="hai-pillar-title">Festival Rundown</strong>
                <p className="hai-pillar-desc">
                  Panduan rundown festival musik multi-hari dan multi-stage yang tersusun rapi per hari.
                </p>
              </div>
            </div>

            <div className="hai-pillar-card">
              <span className="hai-pillar-num">03</span>
              <div className="hai-pillar-info">
                <strong className="hai-pillar-title">Tiket Resmi Terverifikasi</strong>
                <p className="hai-pillar-desc">
                  Rujukan pembelian tiket diarahkan langsung ke loket resmi promotor mitra tepercaya.
                </p>
              </div>
            </div>
          </div>
        </article>

        {/* Tombol Aksi Editorial */}
        <div className="hai-editorial-actions" style={{ marginTop: '36px' }}>
          <button
            type="button"
            className="hai-editorial-btn-primary"
            onClick={() => onNavigate && onNavigate('gigs')}
          >
            Lihat Jadwal Konser
          </button>
          <button
            type="button"
            className="hai-editorial-btn-secondary"
            onClick={() => onNavigate && onNavigate('contact')}
          >
            Kontak Tim (Contact Us)
          </button>
        </div>
      </div>
    </div>
  );
}
