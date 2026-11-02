import React, { useState } from 'react';
import GenreModal from './GenreModal';

export default function FilterBar({
  search,
  setSearch,
  isSearchVisible = false,
  setIsSearchVisible,
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
  const [isGenreModalOpen, setIsGenreModalOpen] = useState(false);

  const VISIBLE_GENRES_LIMIT = 6;
  const topGenres = genres.slice(0, VISIBLE_GENRES_LIMIT);
  const isSelectedInTop = topGenres.some((g) => g.name === selectedGenre);
  const selectedOutsideObj =
    !isSelectedInTop && selectedGenre
      ? genres.find((g) => g.name === selectedGenre) || { name: selectedGenre, id: 'outside-active' }
      : null;
  const hasMoreGenres = genres.length > VISIBLE_GENRES_LIMIT;

  return (
    <section className="filter-section" id="filter-section-root">
      <div className="container">
        {/* Kolom Pencarian yang Terbuka Tepat di Atas Dropdown Wilayah */}
        {isSearchVisible && (
          <div className="filter-search-reveal-box" id="filter-search-box">
            <div className="filter-search-reveal-inner">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" className="filter-search-reveal-icon">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <input
                type="text"
                id="main-gigs-search-input"
                className="filter-search-reveal-input"
                placeholder="Cari artis favorit (The Adams, .Feast), nama gigs, atau venue..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                autoFocus
              />
              {search && (
                <button
                  type="button"
                  className="filter-search-clear-btn"
                  onClick={() => setSearch('')}
                  title="Hapus teks pencarian"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        )}

        {/* Row 1: Filter Controls (Dropdown Wilayah & Free Entry) */}
        <div className="filter-row-primary">
          <div className="filter-controls-group">
            <select
              className="city-select"
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              aria-label="Filter Wilayah"
            >
              <option value="">Semua Wilayah (Jabodetabek)</option>
              {cities.map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>

            <button
              type="button"
              className={`genre-pill free-entry-btn ${isFreeOnly ? 'active' : ''}`}
              onClick={() => setIsFreeOnly(!isFreeOnly)}
              aria-label="Filter Acara Gratis"
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
          >
            <span>Tersimpan</span> {savedCount > 0 ? `(${savedCount})` : ''}
          </button>
        </div>

        {/* Row 3: Genre Tags (Hybrid top pills + '+ Lainnya' Bottom Sheet) */}
        <div className="genre-pills-row">
          <span className="genre-filter-label">
            Genre:
          </span>
          <button
            type="button"
            className={`genre-pill ${selectedGenre === '' ? 'active' : ''}`}
            onClick={() => setSelectedGenre('')}
          >
            Semua
          </button>

          {topGenres.map((g) => (
            <button
              key={g.id}
              type="button"
              className={`genre-pill ${selectedGenre === g.name ? 'active' : ''}`}
              onClick={() => setSelectedGenre(selectedGenre === g.name ? '' : g.name)}
              style={selectedGenre === g.name ? { backgroundColor: g.color || '#ff0055', borderColor: g.color || '#ff0055', color: '#fff' } : {}}
            >
              {g.name}
            </button>
          ))}

          {/* Active outside genre pill if user selected one from the modal */}
          {selectedOutsideObj && (
            <button
              type="button"
              className="genre-pill active genre-pill-outside"
              onClick={() => setSelectedGenre('')}
              style={{
                backgroundColor: selectedOutsideObj.color || '#ff0055',
                borderColor: selectedOutsideObj.color || '#ff0055',
                color: '#fff'
              }}
              title="Klik untuk menghapus filter genre ini"
            >
              <span>{selectedOutsideObj.name}</span>
              <span className="genre-pill-remove-icon" aria-hidden="true">✕</span>
            </button>
          )}

          {/* '+ Lainnya' Button */}
          {hasMoreGenres && (
            <button
              type="button"
              className={`genre-pill genre-more-btn ${selectedOutsideObj ? 'has-active' : ''}`}
              onClick={() => setIsGenreModalOpen(true)}
              aria-label="Lihat semua genre musik"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="4" y1="21" x2="4" y2="14" />
                <line x1="4" y1="10" x2="4" y2="3" />
                <line x1="12" y1="21" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12" y2="3" />
                <line x1="20" y1="21" x2="20" y2="16" />
                <line x1="20" y1="12" x2="20" y2="3" />
                <line x1="1" y1="14" x2="7" y2="14" />
                <line x1="9" y1="8" x2="15" y2="8" />
                <line x1="17" y1="16" x2="23" y2="16" />
              </svg>
              <span>+ Lainnya</span>
              <span className="genre-more-count">({genres.length})</span>
            </button>
          )}
        </div>
      </div>

      {/* Genre Selection Bottom Sheet / Modal */}
      <GenreModal
        isOpen={isGenreModalOpen}
        onClose={() => setIsGenreModalOpen(false)}
        genres={genres}
        selectedGenre={selectedGenre}
        onSelectGenre={setSelectedGenre}
      />
    </section>
  );
}
