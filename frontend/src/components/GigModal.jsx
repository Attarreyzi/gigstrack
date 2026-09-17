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
              <img
                src={
                  detail.display_poster?.startsWith('/media/') || detail.display_poster?.startsWith('/')
                    ? `http://localhost:8000${detail.display_poster}`
                    : (detail.display_poster || "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80")
                }
                alt={detail.title}
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80";
                }}
              />
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
                  {detail.is_free ? 'FREE ADMISSION' : (detail.price_full_range_display || detail.price_range_display || `HTM: IDR ${detail.ticket_price.toLocaleString('id-ID')}`)}
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
                      Open Gate: {(detail.doors_open && detail.doors_open.toUpperCase().includes('TBA')) ? 'TBA' : (detail.doors_open || '18:30 WIB')}
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

              {/* Lineup Musisi Minimalis (Modern Unified Chip Grid) */}
              {detail.lineups && detail.lineups.length > 0 && (
                <div style={{ marginTop: '24px' }}>
                  <h4 style={{ fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '14px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                    </svg>
                    <span>Line-up Band & Musisi ({detail.lineups.length} Artis)</span>
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {detail.lineups.map((item) => (
                      <div
                        key={item.id}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          padding: '7px 14px',
                          borderRadius: '8px',
                          fontSize: '0.88rem',
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid rgba(255, 255, 255, 0.09)',
                          color: 'var(--text-primary)',
                          fontWeight: 500
                        }}
                      >
                        <span>{item.artist?.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Ticket Tiers (Festival / Multi-Price Options) */}
              {detail.ticket_tiers && detail.ticket_tiers.length > 0 && (
                <div style={{ marginTop: '24px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '16px' }}>
                  <h4 style={{ fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '12px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>🎟️</span>
                    <span>Pilihan Kategori & Paket Tiket</span>
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {detail.ticket_tiers.map((tier) => (
                      <div
                        key={tier.id || tier.tier_name}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '10px 14px',
                          background: tier.is_sold_out ? 'rgba(239, 68, 68, 0.06)' : 'rgba(255, 255, 255, 0.02)',
                          border: tier.is_sold_out ? '1px solid rgba(239, 68, 68, 0.2)' : '1px solid rgba(255, 255, 255, 0.06)',
                          borderRadius: '8px',
                          gap: '12px'
                        }}
                      >
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.92rem', color: tier.is_sold_out ? 'var(--text-muted)' : 'var(--text-primary)' }}>
                            {tier.tier_name}
                          </div>
                          {tier.description && (
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                              {tier.description}
                            </div>
                          )}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.95rem', color: tier.is_sold_out ? 'var(--text-muted)' : 'var(--accent-pink)' }}>
                            {tier.price === 0 ? 'GRATIS' : `Rp ${tier.price.toLocaleString('id-ID')}`}
                          </span>
                          <span style={{
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            padding: '3px 8px',
                            borderRadius: '6px',
                            background: tier.is_sold_out ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                            color: tier.is_sold_out ? '#F87171' : '#34D399'
                          }}>
                            {tier.is_sold_out ? 'SOLD OUT' : 'TERSEDIA'}
                          </span>
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
