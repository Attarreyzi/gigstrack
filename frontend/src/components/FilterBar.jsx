import React from 'react';

export default function FilterBar({
  search,
  setSearch,
  selectedCity,
  setSelectedCity,
  selectedGenre,
  setSelectedGenre,
  dateFilter,
  setDateFilter,
  isFreeOnly,
  setIsFreeOnly,
  cities = [],
  genres = [],
  savedCount = 0
}) {
  return (
    <section className="filter-section">
      <div className="container">
        {/* Row 1: Search & City */}
        <div className="filter-row-primary">
          <div className="search-input-wrapper">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input
              type="text"
              className="search-input"
              placeholder="Cari artis (The Adams, .Feast), nama gig, atau venue..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <select
              className="city-select"
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
            >
              <option value="">Semua Wilayah (Jabodetabek)</option>
              {cities.map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>

            <button
              className={`genre-pill ${isFreeOnly ? 'active' : ''}`}
              style={{ padding: '0 16px', display: 'flex', alignItems: 'center', gap: '6px' }}
              onClick={() => setIsFreeOnly(!isFreeOnly)}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                <line x1="7" y1="7" x2="7.01" y2="7"></line>
              </svg>
              <span>Free Entry</span>
            </button>
          </div>
        </div>

        {/* Row 2: Date Tabs */}
        <div className="date-tabs-group" style={{ marginBottom: '14px' }}>
          <button
            className={`date-tab-btn ${dateFilter === 'all' ? 'active' : ''}`}
            onClick={() => setDateFilter('all')}
          >
            Semua Jadwal
          </button>
          <button
            className={`date-tab-btn ${dateFilter === 'today' ? 'active' : ''}`}
            onClick={() => setDateFilter('today')}
          >
            Hari Ini
          </button>
          <button
            className={`date-tab-btn ${dateFilter === 'tomorrow' ? 'active' : ''}`}
            onClick={() => setDateFilter('tomorrow')}
          >
            Besok
          </button>
          <button
            className={`date-tab-btn ${dateFilter === 'this_week' ? 'active' : ''}`}
            onClick={() => setDateFilter('this_week')}
          >
            Minggu Ini
          </button>
          <button
            className={`date-tab-btn ${dateFilter === 'weekend' ? 'active' : ''}`}
            onClick={() => setDateFilter('weekend')}
          >
            Akhir Pekan
          </button>
          <button
            className={`date-tab-btn ${dateFilter === 'saved' ? 'active' : ''}`}
            onClick={() => setDateFilter('saved')}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
            </svg>
            <span>Tersimpan</span>
            {savedCount > 0 && (
              <span style={{
                background: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '10px',
                padding: '1px 6px',
                fontSize: '0.72rem'
              }}>
                {savedCount}
              </span>
            )}
          </button>
        </div>

        {/* Row 3: Genre Tags */}
        <div className="genre-pills-row">
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginRight: '4px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Genre:
          </span>
          <button
            className={`genre-pill ${selectedGenre === '' ? 'active' : ''}`}
            onClick={() => setSelectedGenre('')}
          >
            Semua
          </button>
          {genres.map((g) => (
            <button
              key={g.id}
              className={`genre-pill ${selectedGenre === g.name ? 'active' : ''}`}
              onClick={() => setSelectedGenre(selectedGenre === g.name ? '' : g.name)}
              style={selectedGenre === g.name ? { backgroundColor: g.color, borderColor: g.color, color: '#fff' } : {}}
            >
              {g.name}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
