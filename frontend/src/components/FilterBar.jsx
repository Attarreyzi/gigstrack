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
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input
              type="text"
              className="search-input"
              placeholder="Cari band (The Adams, .Feast), judul acara, atau venue..."
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
              <option value="">📍 Semua Kota</option>
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
              <span>{isFreeOnly ? '✓' : ''}</span>
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
            🔥 Hari Ini
          </button>
          <button
            className={`date-tab-btn ${dateFilter === 'tomorrow' ? 'active' : ''}`}
            onClick={() => setDateFilter('tomorrow')}
          >
            Besok
          </button>
          <button
            className={`date-tab-btn ${dateFilter === 'weekend' ? 'active' : ''}`}
            onClick={() => setDateFilter('weekend')}
          >
            Weekend Ini
          </button>
          <button
            className={`date-tab-btn ${dateFilter === 'saved' ? 'active' : ''}`}
            onClick={() => setDateFilter('saved')}
          >
            ⭐ Tersimpan {savedCount > 0 ? `(${savedCount})` : ''}
          </button>
        </div>

        {/* Row 3: Genre Tags */}
        <div className="genre-pills-row">
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginRight: '4px' }}>
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
              style={selectedGenre === g.name ? { backgroundColor: g.color, borderColor: g.color } : {}}
            >
              {g.name}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
