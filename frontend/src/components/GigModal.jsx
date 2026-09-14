import React, { useEffect, useState } from 'react';
import { fetchGigDetail } from '../services/api';

export default function GigModal({ gigId, onClose, isBookmarked = false, onToggleBookmark = () => {} }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!gigId) return;
    setLoading(true);
    fetchGigDetail(gigId)
      .then((data) => setDetail(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [gigId]);

  // Handle ESC key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!gigId) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose} aria-label="Tutup Modal">
          ✕
        </button>

        {loading ? (
          <div style={{ padding: '80px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: '1.1rem', color: 'var(--text-secondary)' }}>Memuat rincian konser...</div>
          </div>
        ) : detail ? (
          <>
            <div className="modal-poster-hero">
              <img src={detail.display_poster} alt={detail.title} />
              <div className="poster-overlay-gradient"></div>
            </div>

            <div className="modal-body">
              {/* Badges */}
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px', alignItems: 'center' }}>
                {detail.is_happening_today && (
                  <span className="badge-today" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#fff' }}></span>
                    <span>LIVE TONIGHT</span>
                  </span>
                )}
                <span className={`badge-price ${detail.is_free ? 'free' : ''}`}>
                  {detail.is_free ? 'FREE ADMISSION' : `HTM: IDR ${detail.ticket_price.toLocaleString('id-ID')}`}
                </span>
                {detail.status === 'live_now' && (
                  <span className="badge-today" style={{ background: '#FF1744' }}>
                    ON STAGE NOW
                  </span>
                )}
              </div>

              <h2 className="modal-title">{detail.title}</h2>

              {/* Venue & Time Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px', margin: '20px 0' }}>
                <div className="radar-stat-box" style={{ padding: '14px 18px' }}>
                  <div className="stat-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                      <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{detail.venue?.name}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {detail.venue?.address} ({detail.venue?.city})
                    </div>
                  </div>
                </div>

                <div className="radar-stat-box" style={{ padding: '14px 18px' }}>
                  <div className="stat-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                      {new Date(detail.start_datetime).toLocaleDateString('id-ID', {
                        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
                      })}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      Open Gate: {detail.doors_open || '18:30 WIB'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Description */}
              {detail.description && (
                <div style={{ margin: '20px 0', color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: '0.95rem' }}>
                  {detail.description}
                </div>
              )}

              {/* Rundown / Lineup Timetable */}
              {detail.lineups && detail.lineups.length > 0 && (
                <div style={{ marginTop: '24px' }}>
                  <h4 style={{ fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '14px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                    </svg>
                    <span>Line-up & Set Time (Rundown)</span>
                  </h4>
                  <div className="rundown-table">
                    {detail.lineups.map((item) => (
                      <div key={item.id} className="rundown-item">
                        <div className="rundown-band">
                          <img src={item.artist.display_image} alt={item.artist.name} />
                          <div>
                            <div style={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span>{item.artist.name}</span>
                              {item.is_headliner && (
                                <span style={{ background: 'rgba(255, 0, 85, 0.2)', color: 'var(--accent-pink)', fontSize: '0.65rem', padding: '2px 6px', borderRadius: '4px', fontWeight: 800, letterSpacing: '0.04em' }}>
                                  HEADLINER
                                </span>
                              )}
                            </div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                              {item.artist.genres?.map(g => g.name).join(', ')} • Asal: {item.artist.hometown || 'Indonesia'}
                            </div>
                          </div>
                        </div>
                        <div className="rundown-time">
                          {item.set_time || 'TBA'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="modal-actions-row">
                {detail.ticket_url ? (
                  <a
                    href={detail.ticket_url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn-primary"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M2 9a3 3 0 0 1 3-3h14a3 3 0 0 1 3 3v2a3 3 0 0 0 0 6v2a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3v-2a3 3 0 0 0 0-6V9z"></path>
                      <line x1="13" y1="6" x2="13" y2="18"></line>
                    </svg>
                    <span>Beli Tiket Resmi</span>
                  </a>
                ) : detail.is_free ? (
                  <div className="btn-primary" style={{ background: 'linear-gradient(135deg, #00C853, #00E676)', cursor: 'default' }}>
                    <span>Free Admission / Tanpa Tiket</span>
                  </div>
                ) : (
                  <div className="btn-primary" style={{ background: '#252530', cursor: 'default' }}>
                    <span>Tiket On The Spot (OTS)</span>
                  </div>
                )}

                {detail.venue?.maps_url && (
                  <a
                    href={detail.venue.maps_url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn-secondary"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
                    </svg>
                    <span>Google Maps</span>
                  </a>
                )}

                <button
                  className="btn-secondary"
                  onClick={() => onToggleBookmark(detail.id)}
                  style={isBookmarked ? { borderColor: 'var(--accent-pink)', color: 'var(--accent-pink)' } : {}}
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill={isBookmarked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                  </svg>
                  <span>{isBookmarked ? 'Tersimpan' : 'Simpan'}</span>
                </button>
              </div>
            </div>
          </>
        ) : (
          <div style={{ padding: '60px 20px', textAlign: 'center' }}>
            Konser tidak ditemukan.
          </div>
        )}
      </div>
    </div>
  );
}
