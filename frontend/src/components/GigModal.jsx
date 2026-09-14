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
            <div style={{ fontSize: '1.2rem', color: 'var(--text-secondary)' }}>Memuat detail konser...</div>
          </div>
        ) : detail ? (
          <>
            <div className="modal-poster-hero">
              <img src={detail.display_poster} alt={detail.title} />
              <div className="poster-overlay-gradient"></div>
            </div>

            <div className="modal-body">
              {/* Badges */}
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
                {detail.is_happening_today && (
                  <span className="badge-today">🔥 MAIN HARI INI</span>
                )}
                <span className={`badge-price ${detail.is_free ? 'free' : ''}`}>
                  {detail.is_free ? 'GRATIS / FREE ENTRY' : `HTM: Rp ${detail.ticket_price.toLocaleString('id-ID')}`}
                </span>
                {detail.status === 'live_now' && (
                  <span className="badge-today" style={{ background: '#FF1744' }}>🔴 SEDANG BERLANGSUNG</span>
                )}
              </div>

              <h2 className="modal-title">{detail.title}</h2>

              {/* Venue & Time Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px', margin: '20px 0' }}>
                <div className="radar-stat-box" style={{ padding: '12px 16px' }}>
                  <div className="stat-icon" style={{ fontSize: '1.1rem' }}>📍</div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{detail.venue?.name}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {detail.venue?.address} ({detail.venue?.city})
                    </div>
                  </div>
                </div>

                <div className="radar-stat-box" style={{ padding: '12px 16px' }}>
                  <div className="stat-icon" style={{ fontSize: '1.1rem' }}>⏰</div>
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
                  <h4 style={{ fontSize: '1.1rem', marginBottom: '12px', color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>⚡ Line-up & Jadwal Tampil (Rundown)</span>
                  </h4>
                  <div className="rundown-table">
                    {detail.lineups.map((item) => (
                      <div key={item.id} className="rundown-item">
                        <div className="rundown-band">
                          <img src={item.artist.display_image} alt={item.artist.name} />
                          <div>
                            <div style={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span>{item.artist.name}</span>
                              {item.is_headliner && (
                                <span style={{ background: 'rgba(255, 0, 85, 0.2)', color: 'var(--accent-pink)', fontSize: '0.7rem', padding: '2px 6px', borderRadius: '4px' }}>
                                  Headliner
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
                    <span>🎟️ Beli Tiket Resmi</span>
                  </a>
                ) : detail.is_free ? (
                  <div className="btn-primary" style={{ background: 'linear-gradient(135deg, #00C853, #00E676)', cursor: 'default' }}>
                    <span>✓ Free Entry / Tanpa Tiket</span>
                  </div>
                ) : (
                  <div className="btn-primary" style={{ background: '#333', cursor: 'default' }}>
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
                    <span>🗺️ Google Maps</span>
                  </a>
                )}

                <button
                  className="btn-secondary"
                  onClick={() => onToggleBookmark(detail.id)}
                  style={isBookmarked ? { borderColor: 'var(--accent-pink)', color: 'var(--accent-pink)' } : {}}
                >
                  <span>{isBookmarked ? '★ Tersimpan' : '☆ Simpan'}</span>
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
