import React, { useEffect, useState } from 'react';
import { fetchGigsDetail } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function GigModal({ GigsId, gigId, onClose, onRequireAuth }) {
  const targetId = GigsId || gigId;
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [selectedDay, setSelectedDay] = useState('');
  const [isRundownOpen, setIsRundownOpen] = useState(true);
  const { user, isGigSaved, toggleSave } = useAuth();

  useEffect(() => {
    if (!targetId) return;
    setLoading(true);
    fetchGigsDetail(targetId)
      .then((data) => {
        setDetail(data);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [targetId]);

  // Unique Days for multi-day festivals
  const uniqueDays = React.useMemo(() => {
    if (!detail?.lineups) return [];
    const days = [];
    detail.lineups.forEach((l) => {
      const d = (l.day || '').trim();
      if (d && !days.includes(d)) {
        days.push(d);
      }
    });
    return days.sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  }, [detail]);

  // Set default selectedDay ke hari pertama jika festival multi-day
  useEffect(() => {
    if (uniqueDays.length > 1) {
      if (!selectedDay || !uniqueDays.includes(selectedDay)) {
        setSelectedDay(uniqueDays[0]);
      }
    } else {
      setSelectedDay('');
    }
  }, [uniqueDays, selectedDay]);

  const filteredLineups = React.useMemo(() => {
    if (!detail?.lineups) return [];
    let list = [...detail.lineups];
    if (uniqueDays.length > 1 && selectedDay) {
      list = list.filter((l) => (l.day || '').trim() === selectedDay);
    }
    return list.sort((a, b) => {
      const orderA = a.order ?? 999;
      const orderB = b.order ?? 999;
      if (orderA !== orderB) {
        return orderA - orderB;
      }
      return (a.set_time || '').localeCompare(b.set_time || '', undefined, { numeric: true });
    });
  }, [detail, selectedDay, uniqueDays]);

  // Handle ESC key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!targetId) return null;

  const isSaved = detail ? isGigSaved(detail.id) : false;

  const handleCopyCode = (code) => {
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  // Bersihkan deskripsi dari penyebutan lineup yang redundan dengan tabel rundown
  const getCleanDescription = (desc) => {
    if (!desc) return '';
    let cleaned = desc;
    const match = cleaned.search(/(?:\.|\n|\r)?\s*(?:Menghadirkan\s+lineup|Menampilkan\s+lineup|Menghadirkan\s+line-up|Menampilkan\s+line-up|Dimeriahkan\s+oleh|Lineup\s*:|Line-up\s*:)/i);
    if (match !== -1) {
      cleaned = cleaned.substring(0, match).trim();
    }
    cleaned = cleaned.replace(/(?:\.|\n)?\s*Menghadirkan\s+lineup.*$/i, '').trim();
    if (cleaned && !cleaned.endsWith('.')) {
      cleaned += '.';
    }
    return cleaned;
  };

  const mapsQueryUrl = detail?.venue?.maps_url || (detail?.venue ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(detail.venue.name + ' ' + (detail.venue.city || ''))}` : '#');

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
              {/* Badges & Save Toggle */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                  {detail.is_happening_today && (
                    <span className="badge-today" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#fff' }}></span>
                      <span>LIVE TONIGHT</span>
                    </span>
                  )}
                  <span className={`badge-price ${detail.is_free ? 'free' : ''}`}>
                    {detail.is_free
                      ? 'FREE ADMISSION'
                      : (detail.price_full_range_display || detail.price_range_display || (detail.ticket_price > 0 ? `HTM: Rp ${detail.ticket_price.toLocaleString('id-ID')}` : 'Cek Platform Tiket'))}
                  </span>

                  {detail.status === 'live_now' && (
                    <span className="badge-today" style={{ background: '#FF1744' }}>
                      ON STAGE NOW
                    </span>
                  )}
                </div>

                {/* Bookmark Toggle in Modal (Action-gated to Google login) */}
                <button
                  type="button"
                  className={`modal-bookmark-btn ${isSaved ? 'is-saved' : ''}`}
                  onClick={() => {
                    if (!user || user.auth_provider !== 'google') {
                      if (onRequireAuth) onRequireAuth();
                    } else {
                      toggleSave(detail.id);
                    }
                  }}
                  title={isSaved ? "Hapus dari simpanan" : "Simpan konser ini (khusus akun Google)"}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill={isSaved ? "#FF1744" : "none"} stroke={isSaved ? "#FF1744" : "currentColor"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                  </svg>
                  <span>{isSaved ? "Tersimpan" : "Simpan Konser"}</span>
                </button>
              </div>

              <h2 className="modal-title">{detail.title}</h2>

              {/* Clean Editorial Description (No card, no borders) */}
              {detail.description && getCleanDescription(detail.description) && (
                <p className="modal-editorial-desc">
                  {getCleanDescription(detail.description)}
                </p>
              )}

              {/* Venue & Time Grid Second */}
              <div className="modal-meta-grid">
                <a
                  href={mapsQueryUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="radar-stat-box venue-card-link"
                  title="Klik untuk membuka lokasi di Google Maps"
                >
                  <div className="stat-icon" style={{ background: 'rgba(0, 240, 255, 0.12)', color: 'var(--accent-cyan)' }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                      <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                      {detail.venue?.name}
                    </div>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      {detail.venue?.city || 'Jakarta'}
                    </div>
                  </div>
                </a>

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

              {/* Rincian Kategori Tiket & Harga (HTM) */}
              <div style={{ marginTop: '24px' }}>
                <h4 style={{ fontSize: '0.92rem', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '12px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="4" width="20" height="16" rx="2"></rect>
                    <line x1="2" y1="10" x2="22" y2="10"></line>
                  </svg>
                  <span>Rincian Harga & Kategori Tiket</span>
                </h4>

                {detail.ticket_tiers && detail.ticket_tiers.length > 0 ? (
                  <div className="ticket-tiers-grid">
                    {detail.ticket_tiers.map((tier) => (
                      <div key={tier.id} className={`ticket-tier-card ${tier.is_sold_out ? 'sold-out' : ''}`}>
                        <div className="tier-header">
                          <span className="tier-name">{tier.tier_name}</span>
                          <span className={`tier-status-badge ${tier.is_sold_out ? 'status-sold' : 'status-avail'}`}>
                            {tier.is_sold_out ? 'Habis (Sold Out)' : 'Tersedia'}
                          </span>
                        </div>
                        <div className="tier-price">
                          {tier.price > 0 ? `Rp ${tier.price.toLocaleString('id-ID')}` : 'Gratis / Free'}
                        </div>
                        {tier.description && (
                          <div className="tier-desc">{tier.description}</div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : detail.is_free ? (
                  <div className="ticket-free-banner">
                    <span style={{ fontSize: '1.2rem' }}>🎉</span>
                    <div>
                      <strong>Free Admission / Gratis Masuk</strong>
                      <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Acara ini terbuka untuk umum tanpa dipungut biaya tiket masuk.</div>
                    </div>
                  </div>
                ) : (
                  <div className="ticket-tier-single">
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>Tiket Resmi / On The Spot</div>
                      <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Informasi harga dan pembelian tiket dapat dicek melalui platform tiket mitra.</div>
                    </div>
                    <div className="tier-price">
                      {detail.ticket_price > 0 ? `Rp ${detail.ticket_price.toLocaleString('id-ID')}` : 'Cek Platform Tiket'}
                    </div>
                  </div>
                )}
              </div>

              {/* Referral / Voucher Code Section (Only rendered if present) */}
              {detail.referral_code && detail.referral_code.trim() !== '' && (
                <div className="referral-box" style={{ marginTop: '22px' }}>
                  <div className="referral-info">
                    <div className="referral-label">KODE REFERRAL / PROMO TIKET</div>
                    <div className="referral-code-value">
                      {detail.referral_code}
                    </div>
                    <div className="referral-sub">Gunakan kode ini saat checkout di platform tiket untuk promo khusus.</div>
                  </div>
                  <button
                    type="button"
                    className="adm-btn adm-btn-primary referral-copy-btn"
                    onClick={() => handleCopyCode(detail.referral_code)}
                  >
                    {copied ? "✓ Tersalin!" : "Salin Kode"}
                  </button>
                </div>
              )}

              {/* Rundown / Lineup Timetable (Multi-Day Festival Support) */}
              {detail.lineups && detail.lineups.length > 0 && (
                <div style={{ marginTop: '28px' }}>
                  {/* Collapsible Accordion Header */}
                  <div
                    className="rundown-accordion-toggle"
                    onClick={() => setIsRundownOpen(!isRundownOpen)}
                    role="button"
                    tabIndex={0}
                    aria-expanded={isRundownOpen}
                    title={isRundownOpen ? "Tutup rundown" : "Buka susunan rundown"}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <h4 style={{ fontSize: '0.92rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                        </svg>
                        <span>Line-up & Rundown ({detail.lineups.length} Band)</span>
                      </h4>

                      {uniqueDays.length > 1 && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 600, padding: '2px 8px', borderRadius: '999px', background: 'rgba(0, 240, 255, 0.1)' }}>
                          {uniqueDays.length} Hari Festival
                        </span>
                      )}
                    </div>

                    <div className="rundown-accordion-action">
                      <span className="rundown-toggle-hint">
                        {isRundownOpen ? 'Tutup' : 'Lihat Jadwal'}
                      </span>
                      <svg
                        className={`rundown-chevron-icon ${isRundownOpen ? 'open' : ''}`}
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2.4"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <polyline points="6 9 12 15 18 9"></polyline>
                      </svg>
                    </div>
                  </div>

                  {/* Collapsible Content */}
                  {isRundownOpen && (
                    <div className="rundown-accordion-content">
                      {/* Multi-Day Tabs (Hanya Day 1, Day 2, dst. - 'Semua Hari' dihilangkan) */}
                      {uniqueDays.length > 1 && (
                        <div className="rundown-day-tabs">
                          {uniqueDays.map((dayName) => (
                            <button
                              key={dayName}
                              type="button"
                              className={`day-tab-btn ${selectedDay === dayName ? 'active' : ''}`}
                              onClick={() => setSelectedDay(dayName)}
                            >
                              {dayName}
                            </button>
                          ))}
                        </div>
                      )}

                      <div className="rundown-table">
                        {filteredLineups.map((item) => (
                          <div key={item.id} className="rundown-item">
                            <div className="rundown-band">
                              <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#fff' }}>
                                {item.artist?.name}
                              </span>
                            </div>
                            <div className="rundown-time">
                              {item.set_time || 'TBA'}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="modal-actions-row" style={{ marginTop: '26px' }}>
                {detail.ticket_links && detail.ticket_links.length > 0 ? (
                  detail.ticket_links.map((tl, idx) => (
                    <a
                      key={idx}
                      href={tl.url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-primary"
                      style={idx > 0 ? { background: 'linear-gradient(135deg, #7928CA, #4A00E0)' } : {}}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M2 9a3 3 0 0 1 3-3h14a3 3 0 0 1 3 3v2a3 3 0 0 0 0 6v2a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3v-2a3 3 0 0 0 0-6V9z"></path>
                        <line x1="13" y1="6" x2="13" y2="18"></line>
                      </svg>
                      <span>Beli Tiket ({tl.platform_name || 'Platform Tiket'})</span>
                    </a>
                  ))
                ) : detail.ticket_url ? (
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
                    <span>Tiket Tersedia On The Spot (OTS)</span>
                  </div>
                )}
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
