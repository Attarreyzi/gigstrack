import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function GigCard({ Gigs, gig, onSelect, onRequireAuth }) {
  const currentGig = Gigs || gig;
  const { user, isGigSaved, toggleSave } = useAuth();
  if (!currentGig) return null;

  const isSaved = isGigSaved(currentGig.id);

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
    if (currentGig.is_free) return 'FREE ENTRY';
    if (currentGig.price_range_display) {
      if (
        currentGig.price_range_display.includes('Mulai') ||
        currentGig.price_range_display.includes('GRATIS') ||
        currentGig.price_range_display.includes('Cek')
      ) {
        return currentGig.price_range_display;
      }
      return `Mulai ${currentGig.price_range_display}`;
    }
    const p = currentGig.ticket_price || 0;
    if (p > 0) return `Mulai Rp ${p.toLocaleString('id-ID')}`;
    return 'Cek Platform Tiket';
  };

  const mapsQueryUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
    (currentGig.venue_name || '') + ' ' + (currentGig.venue_city || '')
  )}`;

  const MAX_DISPLAY_ARTISTS = 3;
  const totalArtists = currentGig.artists ? currentGig.artists.length : 0;
  const displayedArtists = currentGig.artists ? currentGig.artists.slice(0, MAX_DISPLAY_ARTISTS) : [];
  const remainingArtistsCount = Math.max(0, totalArtists - MAX_DISPLAY_ARTISTS);

  const handleBookmarkClick = (e) => {
    e.stopPropagation();
    if (!user || user.auth_provider !== 'google') {
      if (onRequireAuth) onRequireAuth();
    } else {
      toggleSave(currentGig.id);
    }
  };

  const handleMapsClick = (e) => {
    e.stopPropagation();
    window.open(mapsQueryUrl, '_blank', 'noopener,noreferrer');
  };

  return (
    <article className="gig-card" onClick={() => onSelect(currentGig)}>
      {/* Poster & Badges */}
      <div className="gig-poster-wrapper">
        <img
          src={resolvePosterUrl(currentGig.display_poster)}
          alt={currentGig.title}
          className="gig-poster-img"
          loading="lazy"
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80";
          }}
        />
        <div className="poster-overlay-gradient"></div>

        {/* Top-Left: Status Badge if any */}
        <div className="card-top-left-badge">
          {currentGig.is_happening_today ? (
            <span className="badge-today" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '5px', height: '5px', borderRadius: '50%', backgroundColor: '#fff', display: 'inline-block' }}></span>
              <span>LIVE TONIGHT</span>
            </span>
          ) : (currentGig.ticket_tiers && currentGig.ticket_tiers.length > 1) ? (
            <span className="badge-festival">
              FESTIVAL PASS
            </span>
          ) : null}
        </div>

        {/* Top-Right: Price & Compact Bookmark Button */}
        <div className="card-top-right-group">
          <span className={`badge-price ${currentGig.is_free ? 'free' : ''}`}>
            {formatPriceDisplay()}
          </span>
          <button
            type="button"
            className={`card-bookmark-btn ${isSaved ? 'is-saved' : ''}`}
            onClick={handleBookmarkClick}
            title={isSaved ? "Hapus dari konser tersimpan" : "Simpan konser ini"}
            aria-label="Simpan Konser"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill={isSaved ? "#FF1744" : "none"} stroke={isSaved ? "#FF1744" : "currentColor"} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
            </svg>
          </button>
        </div>
      </div>

      {/* Card Content */}
      <div className="gig-card-body">
        {/* Genres */}
        {currentGig.genres && currentGig.genres.length > 0 && (
          <div className="card-genres">
            {currentGig.genres.slice(0, 3).map((g) => (
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

        <h3 className="gig-card-title">{currentGig.title}</h3>

        {/* Venue & City with clickable Google Maps */}
        <div
          className="gig-meta-item gig-meta-venue clickable-venue"
          onClick={handleMapsClick}
          title="Buka rute di Google Maps"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          <span className="venue-text-link" title={`${currentGig.venue_name || ''} - ${currentGig.venue_city || ''}`}>
            <strong>{currentGig.venue_name}</strong>
            <span className="venue-city-sub"> • {currentGig.venue_city}</span>
          </span>
        </div>

        {/* Date & Time */}
        <div className="gig-meta-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <span className="gig-date-text">
            {formatEventDate(currentGig.start_datetime)} • {
              (currentGig.doors_open && currentGig.doors_open.toUpperCase().includes('TBA'))
                ? 'TBA'
                : (currentGig.doors_open || formatEventTime(currentGig.start_datetime) || 'TBA')
            }
          </span>
        </div>

        {/* Line-up Pills (Condensed with +X lainnya) */}
        {displayedArtists.length > 0 && (
          <div className="card-lineup">
            <div className="lineup-label">Line-up Band:</div>
            <div className="lineup-artist-pills">
              {displayedArtists.map((artist) => (
                <span
                  key={artist.id || artist.name}
                  className="artist-pill"
                >
                  {artist.name}
                </span>
              ))}

              {remainingArtistsCount > 0 && (
                <span
                  className="artist-pill artist-pill-more"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelect(currentGig);
                  }}
                  title="Klik untuk melihat seluruh susunan band penampil di detail"
                >
                  +{remainingArtistsCount} lainnya
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </article>
  );
}
