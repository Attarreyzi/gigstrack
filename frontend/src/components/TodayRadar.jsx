import React from 'react';

export default function TodayRadar({ todayData, stats }) {
  const totalGigs = todayData?.total_gigs_today || 0;
  const dateDisplay = todayData?.date_display || 'Hari Ini';

  return (
    <section className="hero-radar">
      <div className="container">
        <div className="radar-banner">
          <div className="radar-header">
            <div className="radar-live-tag">
              <div className="radar-ping">
                <span></span>
                <span></span>
              </div>
              <span>Live Gig Radar</span>
            </div>
            <div className="radar-date-text" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <span>{dateDisplay}</span>
            </div>
          </div>

          <h1 className="radar-headline">
            {totalGigs > 0 ? (
              <>Ada <span>{totalGigs} Panggung Musik</span> Berlangsung Malam Ini</>
            ) : (
              <>Belum Ada Jadwal Konser <span>Malam Ini</span></>
            )}
          </h1>

          <p className="radar-subtext">
            {totalGigs > 0
              ? 'Pantau jadwal pintu dibuka, susunan tampil band penampil, serta ketersediaan tiket konser independen dan festival lokal terkurasi.'
              : 'Jelajahi agenda konser mendatang melalui filter jadwal atau pilih kota untuk merencanakan akhir pekanmu.'}
          </p>

          <div className="radar-stats-grid">
            {/* Stat 1: Live Gigs */}
            <div className="radar-stat-box">
              <div className="stat-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M2 10v3"></path>
                  <path d="M6 6v11"></path>
                  <path d="M10 3v18"></path>
                  <path d="M14 8v7"></path>
                  <path d="M18 5v13"></path>
                  <path d="M22 10v3"></path>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-number" style={{ color: 'var(--accent-pink)' }}>{totalGigs}</div>
                <div className="stat-label">Gig Hari Ini</div>
              </div>
            </div>

            {/* Stat 2: Artists */}
            <div className="radar-stat-box">
              <div className="stat-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 18V5l12-2v13"></path>
                  <circle cx="6" cy="18" r="3"></circle>
                  <circle cx="18" cy="16" r="3"></circle>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-number">{stats?.total_artists || 7}</div>
                <div className="stat-label">Band / Artis Terdaftar</div>
              </div>
            </div>

            {/* Stat 3: Venues */}
            <div className="radar-stat-box">
              <div className="stat-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-number">{stats?.total_venues || 5}</div>
                <div className="stat-label">Lokasi / Venue</div>
              </div>
            </div>

            {/* Stat 4: Upcoming */}
            <div className="radar-stat-box">
              <div className="stat-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M2 9a3 3 0 0 1 3-3h14a3 3 0 0 1 3 3v2a3 3 0 0 0 0 6v2a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3v-2a3 3 0 0 0 0-6V9z"></path>
                  <line x1="13" y1="6" x2="13" y2="18"></line>
                </svg>
              </div>
              <div className="stat-content">
                <div className="stat-number">{stats?.total_upcoming || 3}</div>
                <div className="stat-label">Jadwal Mendatang</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
