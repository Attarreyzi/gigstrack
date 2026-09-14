import React from 'react';

export default function TodayRadar({ todayData, stats, onSelectGig }) {
  const totalGigs = todayData?.total_gigs_today || 0;
  const dateDisplay = todayData?.date_display || 'Hari Ini';
  const todayGigs = todayData?.gigs || [];

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
            <div className="radar-date-text">
              📅 {dateDisplay}
            </div>
          </div>

          <h1 className="radar-headline">
            {totalGigs > 0 ? (
              <>Ada <span>{totalGigs} Gig Musik</span> Berlangsung Hari Ini!</>
            ) : (
              <>Belum Ada Gig Terjadwal <span>Hari Ini</span></>
            )}
          </h1>

          <p className="radar-subtext">
            {totalGigs > 0
              ? 'Panggung live house dan bar sedang memanas malam ini. Cek jadwal open gate, rundown line-up band, dan amankan tiketmu sebelum kehabisan.'
              : 'Jelajahi konser mendatang di bawah atau cek filter kota untuk menemukan agenda gig akhir pekan ini.'}
          </p>

          <div className="radar-stats-grid">
            <div className="radar-stat-box">
              <div className="stat-icon">🎸</div>
              <div className="stat-content">
                <div className="stat-number" style={{ color: 'var(--accent-pink)' }}>{totalGigs}</div>
                <div className="stat-label">Gig Hari Ini</div>
              </div>
            </div>

            <div className="radar-stat-box">
              <div className="stat-icon">🔥</div>
              <div className="stat-content">
                <div className="stat-number">{stats?.total_artists || 7}</div>
                <div className="stat-label">Band / Artis Terdaftar</div>
              </div>
            </div>

            <div className="radar-stat-box">
              <div className="stat-icon">📍</div>
              <div className="stat-content">
                <div className="stat-number">{stats?.total_venues || 5}</div>
                <div className="stat-label">Live Venues</div>
              </div>
            </div>

            <div className="radar-stat-box">
              <div className="stat-icon">🎟️</div>
              <div className="stat-content">
                <div className="stat-number">{stats?.total_upcoming || 3}</div>
                <div className="stat-label">Konser Mendatang</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
