import React from 'react';

export default function GigCard({ gig, onSelect, isBookmarked = false, onToggleBookmark = () => {} }) {
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

  const resolvePosterUrl = (url) => {
    if (!url) return "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80";
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    if (url.startsWith('/media/') || url.startsWith('/')) {
      return `http://localhost:8000${url}`;
    }
    return url;
  };

  const formatPriceDisplay = () => {
    if (gig.is_free) return 'FREE ENTRY';
    if (gig.price_range_display) {
      if (!gig.price_range_display.toLowerCase().includes('mulai') && !gig.price_range_display.toLowerCase().includes('gratis')) {
        return `Mulai ${gig.price_range_display}`;
      }
      return gig.price_range_display;
    }
    const p = gig.ticket_price || 0;
    if (p === 0) return 'FREE ENTRY';
    return `Mulai Rp ${p.toLocaleString('id-ID')}`;
  };

  return (
    <article className="gig-card" onClick={() => onSelect(gig)}>
      {/* Poster & Badges */}
      <div className="gig-poster-wrapper">
        <img
          src={resolvePosterUrl(gig.display_poster)}
          alt={gig.title}
          className="gig-poster-img"
          loading="lazy"
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80";
          }}
        />
        <div className="poster-overlay-gradient"></div>

        <div className="card-top-badges">
          {gig.is_happening_today ? (
            <span className="badge-today" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#fff', display: 'inline-block' }}></span>
              <span>LIVE TONIGHT</span>
            </span>
          ) : (gig.ticket_tiers && gig.ticket_tiers.length > 1) ? (
            <span style={{ background: 'rgba(139, 92, 246, 0.25)', color: '#C084FC', border: '1px solid rgba(139, 92, 246, 0.4)', padding: '4px 10px', borderRadius: '20px', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.04em' }}>
              FESTIVAL PASS
            </span>
          ) : (
            <span></span>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className={`badge-price ${gig.is_free ? 'free' : ''}`}>
              {formatPriceDisplay()}
            </span>
            <button
              className={`btn-card-bookmark ${isBookmarked ? 'active' : ''}`}
              onClick={(e) => {
                e.stopPropagation();
                onToggleBookmark(gig.id);
              }}
              title={isBookmarked ? "Hapus dari favorit" : "Simpan ke favorit"}
              aria-label="Bookmark gig"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill={isBookmarked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
              </svg>
            </button>
          </div>
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
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          <span><strong>{gig.venue_name}</strong> • {gig.venue_city}</span>
        </div>

        {/* Date & Time */}
        <div className="gig-meta-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <span>
            {formatEventDate(gig.start_datetime)} • {
              (gig.doors_open && gig.doors_open.toUpperCase().includes('TBA'))
                ? 'TBA'
                : (gig.doors_open || formatEventTime(gig.start_datetime) || 'TBA')
            }
          </span>
        </div>

        {/* Line-up Pills (Modern Unified Clean Badges) */}
        {gig.artists && gig.artists.length > 0 && (
          <div className="card-lineup">
            <div className="lineup-label">Line-up Band:</div>
            <div className="lineup-artist-pills">
              {gig.artists.map((artist) => (
                <span
                  key={artist.id}
                  className="artist-pill"
                  title={artist.name}
                  style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.09)',
                    color: 'var(--text-secondary)',
                    fontWeight: 500
                  }}
                >
                  <span>{artist.name}</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </article>
  );
}
