import React, { useState, useEffect } from 'react';
import { fetchPublicArtists } from '../services/api';

export default function ArtistsCatalog({ onSelectArtist }) {
  const [artists, setArtists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    let active = true;
    const timer = setTimeout(() => {
      setLoading(true);
      fetchPublicArtists({ search })
        .then((data) => {
          if (active) {
            setArtists(data || []);
            setLoading(false);
          }
        })
        .catch(() => {
          if (active) setLoading(false);
        });
    }, 250);

    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [search]);

  return (
    <section id="artists-section" className="artists-catalog-section">
      <div className="container">
        <div className="artists-section-header">
          <div>
            <div className="section-badge-tag">
              <span className="dot-pulse"></span>
              <span>Katalog Band & Musisi</span>
            </div>
            <h2 className="section-main-title">Eksplorasi Musisi & Band Lokal</h2>
            <p className="section-subtitle">
              Kenali musisi independen, line-up festival, genre musik, dan temukan jadwal panggung konser mereka selanjutnya.
            </p>
          </div>

          <div className="artists-search-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input
              type="text"
              placeholder="Cari band (Dewa 19, Hindia, Feast...)"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="artists-cards-grid">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="artist-card-skeleton"></div>
            ))}
          </div>
        ) : artists.length > 0 ? (
          <div className="artists-cards-grid">
            {artists.map((artist) => (
              <div key={artist.id} className="public-artist-card">
                <div className="artist-avatar-wrap">
                  <img
                    src={artist.display_image || "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80"}
                    alt={artist.name}
                    loading="lazy"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80";
                    }}
                  />
                  {artist.is_active && (
                    <span className="artist-live-indicator" title="Aktif di skena konser">
                      <span></span>
                    </span>
                  )}
                </div>

                <div className="artist-card-body">
                  <div className="artist-name-row">
                    <h3 className="artist-name">{artist.name}</h3>
                    {artist.hometown && (
                      <span className="artist-city-tag">📍 {artist.hometown}</span>
                    )}
                  </div>

                  {artist.genres && artist.genres.length > 0 && (
                    <div className="artist-genre-chips">
                      {artist.genres.slice(0, 3).map((g) => (
                        <span
                          key={g.id || g.name}
                          className="artist-genre-chip"
                          style={{
                            borderColor: (g.color || '#FF3366') + '55',
                            color: g.color || '#FF3366',
                            background: (g.color || '#FF3366') + '15',
                          }}
                        >
                          {g.name}
                        </span>
                      ))}
                    </div>
                  )}

                  {artist.bio && (
                    <p className="artist-bio-snippet">
                      {artist.bio.length > 95 ? `${artist.bio.slice(0, 95)}...` : artist.bio}
                    </p>
                  )}

                  <div className="artist-card-footer">
                    <button
                      type="button"
                      className="artist-gigs-btn"
                      onClick={() => onSelectArtist(artist.name)}
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                        <circle cx="12" cy="10" r="3"></circle>
                      </svg>
                      <span>Cari Jadwal Panggung ↗</span>
                    </button>

                    <div className="artist-socials">
                      {artist.spotify_url && (
                        <a href={artist.spotify_url} target="_blank" rel="noreferrer" title="Spotify" className="social-icon-btn">
                          🎵
                        </a>
                      )}
                      {artist.instagram_url && (
                        <a href={artist.instagram_url} target="_blank" rel="noreferrer" title="Instagram" className="social-icon-btn">
                          📷
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="radar-empty-state" style={{ margin: '30px 0' }}>
            <p>Tidak ditemukan musisi atau band dengan kata kunci "{search}".</p>
          </div>
        )}
      </div>
    </section>
  );
}
