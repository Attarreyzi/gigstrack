import React from 'react';

export default function GigCard({ gig, onSelect }) {
  // Format datetime
  const formatEventDate = (datetimeStr) => {
    try {
      const dt = new Date(datetimeStr);
      return dt.toLocaleDateString('id-ID', {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    } catch {
      return datetimeStr;
    }
  };

  const formatEventTime = (datetimeStr) => {
    try {
      const dt = new Date(datetimeStr);
      return dt.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WIB';
    } catch {
      return '';
    }
  };

  return (
    <article className="gig-card" onClick={() => onSelect(gig)}>
      {/* Poster & Badges */}
      <div className="gig-poster-wrapper">
        <img
          src={gig.display_poster}
          alt={gig.title}
          className="gig-poster-img"
          loading="lazy"
        />
        <div className="poster-overlay-gradient"></div>

        <div className="card-top-badges">
          {gig.is_happening_today ? (
            <span className="badge-today">
              🔥 HARI INI
            </span>
          ) : (
            <span></span>
          )}

          <span className={`badge-price ${gig.is_free ? 'free' : ''}`}>
            {gig.is_free ? 'FREE ENTRY' : `Rp ${gig.ticket_price.toLocaleString('id-ID')}`}
          </span>
        </div>
      </div>

      {/* Card Content */}
      <div className="gig-card-body">
        {/* Genres */}
        {gig.genres && gig.genres.length > 0 && (
          <div className="card-genres">
            {gig.genres.slice(0, 3).map((g) => (
              <span
                key={g.id || g.name}
                className="genre-tag"
                style={{ color: g.color || '#fff' }}
              >
                {g.name}
              </span>
            ))}
          </div>
        )}

        <h3 className="gig-card-title">{gig.title}</h3>

        {/* Venue & City */}
        <div className="gig-meta-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          <span><strong>{gig.venue_name}</strong> • {gig.venue_city}</span>
        </div>

        {/* Date & Time */}
        <div className="gig-meta-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <span>{formatEventDate(gig.start_datetime)} ({gig.doors_open || formatEventTime(gig.start_datetime)})</span>
        </div>

        {/* Line-up Pills */}
        {gig.artists && gig.artists.length > 0 && (
          <div className="card-lineup">
            <div className="lineup-label">Line-up Band:</div>
            <div className="lineup-artist-pills">
              {gig.artists.map((artist) => (
                <span
                  key={artist.id}
                  className={`artist-pill ${artist.is_headliner ? 'headliner' : ''}`}
                  title={artist.name}
                >
                  <img src={artist.image} alt={artist.name} />
                  <span>{artist.name}</span>
                  {artist.is_headliner && <span style={{ color: 'var(--accent-pink)', fontSize: '0.65rem' }}>★</span>}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </article>
  );
}
