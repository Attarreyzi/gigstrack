import React, { useState, useEffect, useRef } from 'react';

export default function GenreModal({
  isOpen,
  onClose,
  genres = [],
  selectedGenre = '',
  onSelectGenre
}) {
  const [search, setSearch] = useState('');
  const searchInputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setSearch('');
      const timer = setTimeout(() => {
        if (searchInputRef.current) searchInputRef.current.focus();
      }, 150);

      const originalOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';

      const handleKeyDown = (e) => {
        if (e.key === 'Escape') onClose();
      };
      window.addEventListener('keydown', handleKeyDown);

      return () => {
        clearTimeout(timer);
        document.body.style.overflow = originalOverflow;
        window.removeEventListener('keydown', handleKeyDown);
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filteredGenres = genres.filter((g) =>
    g.name.toLowerCase().includes(search.trim().toLowerCase())
  );

  const handleSelect = (genreName) => {
    if (selectedGenre === genreName) {
      onSelectGenre('');
    } else {
      onSelectGenre(genreName);
    }
    onClose();
  };

  return (
    <div className="genre-modal-backdrop" onClick={onClose}>
      <div
        className="genre-modal-content"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="genre-modal-title"
      >
        {/* Mobile Drag Indicator Handle */}
        <div className="genre-modal-drag-handle" />

        {/* Modal Header */}
        <div className="genre-modal-header">
          <div className="genre-modal-header-left">
            <div className="genre-modal-icon-badge">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 18V5l12-2v13" />
                <circle cx="6" cy="18" r="3" />
                <circle cx="18" cy="16" r="3" />
              </svg>
            </div>
            <div>
              <h3 id="genre-modal-title" className="genre-modal-title">
                Semua Genre Musik
              </h3>
              <p className="genre-modal-subtitle">
                Pilih genre untuk memfilter jadwal gigs & festival
              </p>
            </div>
          </div>
          <button
            type="button"
            className="genre-modal-close-btn"
            onClick={onClose}
            aria-label="Tutup"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="18" x2="18" y2="6" />
            </svg>
          </button>
        </div>

        {/* Search Input Box */}
        <div className="genre-modal-search-wrapper">
          <svg className="genre-modal-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            ref={searchInputRef}
            type="text"
            className="genre-modal-search-input"
            placeholder="Cari genre (Rock, Pop, Jazz, Metal...)"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button
              type="button"
              className="genre-modal-search-clear"
              onClick={() => setSearch('')}
              aria-label="Hapus pencarian"
            >
              ✕
            </button>
          )}
        </div>

        {/* Quick Row: Semua Genre & Total Count */}
        <div className="genre-modal-quick-row">
          <button
            type="button"
            className={`genre-modal-quick-pill ${selectedGenre === '' ? 'active' : ''}`}
            onClick={() => handleSelect('')}
          >
            <span>Semua Genre</span>
            {selectedGenre === '' && (
              <span className="genre-check-indicator">✓</span>
            )}
          </button>
          <span className="genre-modal-count-badge">
            {filteredGenres.length} Genre {search ? 'ditemukan' : 'tersedia'}
          </span>
        </div>

        {/* Scrollable Genre Grid */}
        <div className="genre-modal-scrollable">
          {filteredGenres.length > 0 ? (
            <div className="genre-modal-grid">
              {filteredGenres.map((g) => {
                const isActive = selectedGenre === g.name;
                const accentColor = g.color || '#ff0055';
                return (
                  <button
                    key={g.id || g.name}
                    type="button"
                    className={`genre-grid-item ${isActive ? 'active' : ''}`}
                    onClick={() => handleSelect(g.name)}
                    style={
                      isActive
                        ? {
                            borderColor: accentColor,
                            boxShadow: `0 0 16px ${accentColor}33`,
                            backgroundColor: 'rgba(255, 255, 255, 0.08)'
                          }
                        : {}
                    }
                  >
                    <span
                      className="genre-grid-color-dot"
                      style={{
                        backgroundColor: accentColor,
                        boxShadow: `0 0 8px ${accentColor}80`
                      }}
                    />
                    <span className="genre-grid-name">{g.name}</span>
                    {isActive && (
                      <span className="genre-grid-check" style={{ color: accentColor }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="genre-modal-empty">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
                <line x1="8" y1="11" x2="14" y2="11" />
              </svg>
              <p>Tidak ada genre yang cocok dengan "{search}"</p>
              <button
                type="button"
                className="genre-modal-reset-search-btn"
                onClick={() => setSearch('')}
              >
                Reset Pencarian
              </button>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="genre-modal-footer">
          <div className="genre-modal-footer-status">
            <span>Filter Aktif:</span>{' '}
            <strong style={{ color: selectedGenre ? 'var(--accent-pink)' : '#fff' }}>
              {selectedGenre || 'Semua Genre'}
            </strong>
          </div>
          <div className="genre-modal-footer-actions">
            {selectedGenre && (
              <button
                type="button"
                className="genre-modal-reset-btn"
                onClick={() => handleSelect('')}
              >
                Reset Filter
              </button>
            )}
            <button
              type="button"
              className="genre-modal-done-btn"
              onClick={onClose}
            >
              Tutup
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
