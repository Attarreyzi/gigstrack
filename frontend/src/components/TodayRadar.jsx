import React from 'react';

export default function TodayRadar({ todayData, stats, onSelectDateFilter, onSelectTab }) {
  const totalGigs = todayData?.total_gigs_today ?? todayData?.total_Gigss_today ?? 0;
  const dateDisplay = todayData?.date_display || 'Hari Ini';

  const handleFilterToday = () => {
    if (onSelectDateFilter) {
      onSelectDateFilter('today');
      const el = document.getElementById('gigs-listing-section');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleFilterWeekend = () => {
    if (onSelectDateFilter) {
      onSelectDateFilter('weekend');
      const el = document.getElementById('gigs-listing-section');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleOpenArtists = () => {
    if (onSelectTab) {
      onSelectTab('artists');
      const el = document.getElementById('artists-section');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleScrollAll = () => {
    if (onSelectDateFilter) onSelectDateFilter('all');
    if (onSelectTab) onSelectTab('gigs');
    const el = document.getElementById('gigs-listing-section');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

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
              <span>Live Music Radar</span>
            </div>
            <div className="radar-date-text">
              <span>{dateDisplay}</span>
            </div>
          </div>

          <h1 className="radar-headline">
            {totalGigs > 0 ? (
              <>Ada <span>{totalGigs} Panggung Musik</span> Berlangsung Hari Ini</>
            ) : (
              <>Radar Panggung Musik & Konser Independen</>
            )}
          </h1>

          <p className="radar-subtext" style={{ marginBottom: 0 }}>
            Pantau jadwal buka panggung, susunan line-up musisi lokal, serta tiket konser festival terkurasi secara langsung.
          </p>
        </div>
      </div>
    </section>
  );
}
