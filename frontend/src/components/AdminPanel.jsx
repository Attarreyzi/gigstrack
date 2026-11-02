import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  fetchAdminStats, fetchAdminGigss, createAdminGigs, updateAdminGigs, deleteAdminGigs,
  fetchAdminArtists, createAdminArtist, updateAdminArtist, deleteAdminArtist,
  fetchAdminVenues, createAdminVenue, updateAdminVenue, deleteAdminVenue,
  fetchAdminGenres, createAdminGenre, updateAdminGenre, deleteAdminGenre,
  fetchAdminUsers, updateAdminUser, deleteAdminUser,
  addAdminLineup, removeAdminLineup,
} from '../services/api';

const STATUS_COLORS = {
  scheduled: '#2196F3', live_now: '#FF1744',
  completed: '#9E9E9E', postponed: '#FF9100', cancelled: '#D50000',
};
const STATUS_LABELS = {
  scheduled: 'Dijadwalkan', live_now: 'Live Sekarang',
  completed: 'Selesai', postponed: 'Ditunda', cancelled: 'Dibatalkan',
};

function StatCard({ icon, label, value, sub, color }) {
  return (
    <div className="adm-stat-card" style={{ '--stat-color': color }}>
      <div className="adm-stat-icon">{icon}</div>
      <div className="adm-stat-body">
        <div className="adm-stat-value">{value}</div>
        <div className="adm-stat-label">{label}</div>
        {sub && <div className="adm-stat-sub">{sub}</div>}
      </div>
    </div>
  );
}

function ConfirmDialog({ message, onConfirm, onCancel }) {
  return (
    <div className="adm-confirm-overlay">
      <div className="adm-confirm-box">
        <div className="adm-confirm-icon">⚠️</div>
        <p>{message}</p>
        <div className="adm-confirm-actions">
          <button className="adm-btn adm-btn-ghost" onClick={onCancel}>Batal</button>
          <button className="adm-btn adm-btn-danger" onClick={onConfirm}>Hapus</button>
        </div>
      </div>
    </div>
  );
}

function Toast({ message, type, onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 3500);
    return () => clearTimeout(t);
  }, [onClose]);
  return (
    <div className={`adm-toast adm-toast-${type}`}>
      <span>{type === 'success' ? '✓' : '✗'}</span>
      {message}
    </div>
  );
}

// ─── Dashboard Panel ──────────────────────────────────────────────────────────
function DashboardPanel({ stats }) {
  if (!stats) return <div className="adm-loading">Memuat statistik...</div>;
  return (
    <div className="adm-dashboard">
      <div className="adm-stats-grid">
        <StatCard icon="🎸" label="Total Gigs" value={stats.Gigss.total} sub={`${stats.Gigss.today} hari ini`} color="#ff0055" />
        <StatCard icon="📅" label="Gigs Mendatang" value={stats.Gigss.upcoming} sub="status: scheduled" color="#00f0ff" />
        <StatCard icon="⭐" label="Gigs Featured" value={stats.Gigss.featured} sub="di banner utama" color="#ff9900" />
        <StatCard icon="🎤" label="Total Artis" value={stats.artists.total} sub={`${stats.artists.active} aktif`} color="#7928ca" />
        <StatCard icon="🏟️" label="Total Venue" value={stats.venues.total} sub="venue terdaftar" color="#00e676" />
        <StatCard icon="👥" label="Total User" value={stats.users.total} sub={`${stats.users.staff} staff/admin`} color="#2196f3" />
      </div>

      <div className="adm-dashboard-grid">
        <div className="adm-card">
          <h3 className="adm-card-title">Status Breakdown</h3>
          <div className="adm-status-list">
            {Object.entries(stats.Gigss.status_breakdown).map(([s, count]) => (
              <div key={s} className="adm-status-item">
                <span className="adm-status-badge" style={{ background: STATUS_COLORS[s] || '#555' }}>
                  {STATUS_LABELS[s] || s}
                </span>
                <span className="adm-status-count">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="adm-card adm-recent-Gigss">
          <h3 className="adm-card-title">Gigs Terbaru Ditambahkan</h3>
          <div className="adm-recent-list">
            {stats.recent_Gigss.map(Gigs => (
              <div key={Gigs.id} className="adm-recent-item">
                <img src={Gigs.poster} alt={Gigs.title} className="adm-recent-poster" />
                <div className="adm-recent-info">
                  <div className="adm-recent-title">{Gigs.title}</div>
                  <div className="adm-recent-meta">{Gigs.venue} - {Gigs.city}</div>
                  <div className="adm-recent-date">{Gigs.start_datetime}</div>
                </div>
                <span className="adm-status-badge" style={{ background: STATUS_COLORS[Gigs.status] || '#555' }}>
                  {STATUS_LABELS[Gigs.status] || Gigs.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Gigss Panel ───────────────────────────────────────────────────────────────
function GigssPanel({ showToast }) {
  const [Gigss, setGigss] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [editGigs, setEditGigs] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [venues, setVenues] = useState([]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      const data = await fetchAdminGigss(params);
      setGigss(data.results || data);
    } catch (e) {
      showToast(e.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
  }, [load]);

  useEffect(() => {
    fetchAdminVenues({ active: 'true' })
      .then(d => setVenues(d.results || d))
      .catch(() => { });
  }, []);

  const handleDelete = async (id) => {
    try {
      await deleteAdminGigs(id);
      showToast('Gigs berhasil dihapus.', 'success');
      load();
    } catch (e) {
      showToast(e.message, 'error');
    }
    setConfirmDelete(null);
  };

  return (
    <div className="adm-panel">
      {confirmDelete && (
        <ConfirmDialog
          message={`Hapus Gigs "${confirmDelete.title}"? Tindakan ini tidak bisa dibatalkan.`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}

      <div className="adm-panel-header">
        <div className="adm-panel-search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
          <input placeholder="Cari Gigs, venue, artis..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <button className="adm-btn adm-btn-primary" onClick={() => { setEditGigs(null); setShowForm(true); }}>
          + Tambah Gigs
        </button>
      </div>

      {showForm && (
        <GigsForm
          Gigs={editGigs}
          venues={venues}
          onClose={() => { setShowForm(false); setEditGigs(null); }}
          onSaved={() => { setShowForm(false); setEditGigs(null); load(); showToast('Gigs berhasil disimpan!', 'success'); }}
          showToast={showToast}
        />
      )}

      {loading ? (
        <div className="adm-loading">Memuat data Gigs...</div>
      ) : (
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead>
              <tr>
                <th>Poster</th><th>Nama Gigs</th><th>Venue & Kota</th>
                <th>Tanggal</th><th>Harga</th><th>Status</th><th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              {Gigss.length === 0 ? (
                <tr><td colSpan={7} className="adm-empty">Tidak ada Gigs ditemukan.</td></tr>
              ) : Gigss.map(Gigs => (
                <tr key={Gigs.id}>
                  <td><img src={Gigs.display_poster} alt={Gigs.title} className="adm-table-poster" /></td>
                  <td>
                    <div className="adm-table-name">{Gigs.title}</div>
                    {Gigs.is_featured && <span className="adm-badge-featured">⭐ Featured</span>}
                  </td>
                  <td>
                    <div className="adm-table-venue">{Gigs.venue_name}</div>
                    <div className="adm-table-city">{Gigs.venue_city}</div>
                  </td>
                  <td className="adm-table-date">{new Date(Gigs.start_datetime).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</td>
                  <td>
                    {Gigs.is_free
                      ? <span className="adm-badge-free">FREE</span>
                      : <span>Rp {Number(Gigs.ticket_price || 0).toLocaleString('id-ID')}</span>
                    }
                  </td>
                  <td>
                    <span className="adm-status-badge" style={{ background: STATUS_COLORS[Gigs.status] || '#555' }}>
                      {STATUS_LABELS[Gigs.status] || Gigs.status}
                    </span>
                  </td>
                  <td>
                    <div className="adm-actions">
                      <button className="adm-btn-icon adm-btn-edit" title="Edit" onClick={() => { setEditGigs(Gigs); setShowForm(true); }}>✏️</button>
                      <button className="adm-btn-icon adm-btn-del" title="Hapus" onClick={() => setConfirmDelete(Gigs)}>🗑️</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function GigsForm({ Gigs, venues, onClose, onSaved, showToast }) {
  const [form, setForm] = useState({
    title: Gigs?.title || '',
    venue: Gigs?.venue || '',
    start_datetime: Gigs?.start_datetime ? Gigs.start_datetime.slice(0, 16) : '',
    end_datetime: Gigs?.end_datetime ? Gigs.end_datetime.slice(0, 16) : '',
    doors_open: Gigs?.doors_open || '18:30 WIB',
    description: Gigs?.description || '',
    ticket_price: Gigs?.ticket_price || 0,
    is_free: Gigs?.is_free || false,
    ticket_url: Gigs?.ticket_url || '',
    status: Gigs?.status || 'scheduled',
    is_featured: Gigs?.is_featured || false,
    poster_url: Gigs?.poster_url || '',
    referral_code: Gigs?.referral_code || '',
  });
  const [saving, setSaving] = useState(false);

  // Multi-day Lineup management states
  const [lineups, setLineups] = useState(Gigs?.lineups || []);
  const [artistsList, setArtistsList] = useState([]);
  const [selectedArtistId, setSelectedArtistId] = useState('');
  const [lineupDay, setLineupDay] = useState('Day 1');
  const [lineupTime, setLineupTime] = useState('18:00 WIB');
  const [lineupIsHeadliner, setLineupIsHeadliner] = useState(false);
  const [addingLineup, setAddingLineup] = useState(false);

  useEffect(() => {
    fetchAdminArtists({ active: 'true' })
      .then(d => setArtistsList(d.results || d))
      .catch(() => {});
  }, []);

  const handleAddLineup = async (e) => {
    e.preventDefault();
    if (!Gigs?.id) {
      showToast('Simpan Gigs terlebih dahulu sebelum menambah lineup.', 'error');
      return;
    }
    if (!selectedArtistId) {
      showToast('Pilih artis terlebih dahulu.', 'error');
      return;
    }
    setAddingLineup(true);
    try {
      const payload = {
        artist: Number(selectedArtistId),
        day: lineupDay.trim(),
        set_time: lineupTime.trim() || 'TBA',
        is_headliner: lineupIsHeadliner,
        order: lineups.length + 1
      };
      const res = await addAdminLineup(Gigs.id, payload);
      setLineups(prev => [...prev, res]);
      setSelectedArtistId('');
      showToast('Artis berhasil ditambahkan ke lineup rundown!', 'success');
    } catch (err) {
      showToast('Gagal menambah lineup: ' + err.message, 'error');
    } finally {
      setAddingLineup(false);
    }
  };

  const handleRemoveLineup = async (lineupId) => {
    if (!Gigs?.id) return;
    try {
      await removeAdminLineup(Gigs.id, lineupId);
      setLineups(prev => prev.filter(l => l.id !== lineupId));
      showToast('Lineup berhasil dihapus.', 'success');
    } catch (err) {
      showToast('Gagal menghapus lineup: ' + err.message, 'error');
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (Gigs) {
        await updateAdminGigs(Gigs.id, form);
      } else {
        await createAdminGigs(form);
      }
      onSaved();
    } catch (err) {
      showToast('Gagal menyimpan: ' + err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="adm-form-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="adm-form-panel">
        <div className="adm-form-header">
          <h2>{Gigs ? '✏️ Edit Gigs' : '➕ Tambah Gigs Baru'}</h2>
          <button className="adm-form-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="adm-form">
          <div className="adm-form-grid">
            <div className="adm-form-field adm-span-2">
              <label>Nama Gigs / Acara *</label>
              <input name="title" value={form.title} onChange={handleChange} placeholder="Nama acara..." required />
            </div>
            <div className="adm-form-field">
              <label>Venue *</label>
              <select name="venue" value={form.venue} onChange={handleChange} required>
                <option value="">-- Pilih Venue --</option>
                {venues.map(v => <option key={v.id} value={v.id}>{v.name} ({v.city})</option>)}
              </select>
            </div>
            <div className="adm-form-field">
              <label>Status</label>
              <select name="status" value={form.status} onChange={handleChange}>
                {Object.entries(STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
            <div className="adm-form-field">
              <label>Waktu Mulai *</label>
              <input type="datetime-local" name="start_datetime" value={form.start_datetime} onChange={handleChange} required />
            </div>
            <div className="adm-form-field">
              <label>Waktu Selesai</label>
              <input type="datetime-local" name="end_datetime" value={form.end_datetime} onChange={handleChange} />
            </div>
            <div className="adm-form-field">
              <label>Open Gate / Doors Open</label>
              <input name="doors_open" value={form.doors_open} onChange={handleChange} placeholder="18:30 WIB" />
            </div>
            <div className="adm-form-field">
              <label>Harga Tiket (Rp)</label>
              <input type="number" name="ticket_price" value={form.ticket_price} onChange={handleChange} min="0" />
            </div>
            <div className="adm-form-field adm-span-2">
              <label>URL Poster</label>
              <input name="poster_url" value={form.poster_url} onChange={handleChange} placeholder="https://..." />
            </div>
            <div className="adm-form-field adm-span-2">
              <label>Link Tiket / RSVP</label>
              <input name="ticket_url" value={form.ticket_url} onChange={handleChange} placeholder="https://loket.com/..." />
            </div>
            <div className="adm-form-field adm-span-2">
              <label>Kode Referral / Promo (Opsional)</label>
              <input
                name="referral_code"
                value={form.referral_code}
                onChange={handleChange}
                placeholder="Contoh: REMEMBERFEST10, EARLYBIRD (Kosongkan jika tidak ada promo)"
              />
            </div>
            <div className="adm-form-field adm-span-2">
              <label>Deskripsi Acara</label>
              <textarea name="description" value={form.description} onChange={handleChange} rows="3" placeholder="Deskripsi singkat acara..." />
            </div>
            <div className="adm-form-field adm-checkboxes">
              <label className="adm-checkbox-label">
                <input type="checkbox" name="is_free" checked={form.is_free} onChange={handleChange} />
                Gratis / Free Entry
              </label>
              <label className="adm-checkbox-label">
                <input type="checkbox" name="is_featured" checked={form.is_featured} onChange={handleChange} />
                Featured di Banner Utama
              </label>
            </div>

            {/* Multi-Day Lineup & Rundown Festival Manager */}
            {Gigs && (
              <div className="adm-form-field adm-span-2" style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <label style={{ fontSize: '0.92rem', fontWeight: 700, color: '#fff', margin: 0 }}>
                    Susunan Lineup & Rundown Festival ({lineups.length} Artis)
                  </label>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    Mendukung multi-day (Day 1, Day 2, Day 3)
                  </span>
                </div>

                {/* Table of current lineups */}
                {lineups.length > 0 ? (
                  <div className="adm-table-wrap" style={{ maxHeight: '220px', overflowY: 'auto', marginBottom: '16px' }}>
                    <table className="adm-table" style={{ fontSize: '0.84rem' }}>
                      <thead>
                        <tr>
                          <th>Artis / Band</th>
                          <th>Hari / Day</th>
                          <th>Jam Tampil</th>
                          <th>Status</th>
                          <th>Aksi</th>
                        </tr>
                      </thead>
                      <tbody>
                        {lineups.map(l => (
                          <tr key={l.id}>
                            <td style={{ fontWeight: 600 }}>{l.artist_name || l.artist?.name}</td>
                            <td>
                              {l.day ? (
                                <span className="adm-status-badge" style={{ background: '#00f0ff22', color: '#00f0ff', border: '1px solid #00f0ff55' }}>
                                  {l.day}
                                </span>
                              ) : <span style={{ color: 'var(--text-muted)' }}>—</span>}
                            </td>
                            <td style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>{l.set_time || 'TBA'}</td>
                            <td>
                              {l.is_headliner ? (
                                <span className="adm-status-badge" style={{ background: '#ff005522', color: '#ff0055', border: '1px solid #ff005555' }}>
                                  Headliner
                                </span>
                              ) : <span style={{ color: 'var(--text-muted)' }}>Lineup</span>}
                            </td>
                            <td>
                              <button
                                type="button"
                                className="adm-btn-icon adm-btn-del"
                                onClick={() => handleRemoveLineup(l.id)}
                                title="Hapus artis ini dari lineup"
                              >
                                🗑️
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div style={{ padding: '14px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', color: 'var(--text-muted)', fontSize: '0.84rem', marginBottom: '16px', textAlign: 'center' }}>
                    Belum ada lineup band yang ditambahkan ke acara ini.
                  </div>
                )}

                {/* Add new lineup sub-form */}
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '10px' }}>
                    + Tambah Musisi / Rundown
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', alignItems: 'end' }}>
                    <div>
                      <label style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Pilih Artis</label>
                      <select
                        value={selectedArtistId}
                        onChange={e => setSelectedArtistId(e.target.value)}
                        style={{ width: '100%', padding: '8px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', fontSize: '0.82rem' }}
                      >
                        <option value="">-- Pilih Artis --</option>
                        {artistsList.map(a => (
                          <option key={a.id} value={a.id}>{a.name}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Hari / Day</label>
                      <input
                        type="text"
                        value={lineupDay}
                        onChange={e => setLineupDay(e.target.value)}
                        placeholder="Day 1 / 25 Des"
                        style={{ width: '100%', padding: '8px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', fontSize: '0.82rem' }}
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Jam Tampil</label>
                      <input
                        type="text"
                        value={lineupTime}
                        onChange={e => setLineupTime(e.target.value)}
                        placeholder="19:30 WIB"
                        style={{ width: '100%', padding: '8px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)', color: '#fff', fontSize: '0.82rem' }}
                      />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', height: '36px' }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                        <input
                          type="checkbox"
                          checked={lineupIsHeadliner}
                          onChange={e => setLineupIsHeadliner(e.target.checked)}
                        />
                        Headliner
                      </label>
                    </div>

                    <div>
                      <button
                        type="button"
                        className="adm-btn adm-btn-primary"
                        onClick={handleAddLineup}
                        disabled={addingLineup || !selectedArtistId}
                        style={{ width: '100%', padding: '8px 12px', fontSize: '0.82rem' }}
                      >
                        {addingLineup ? 'Menambahkan...' : '+ Tambah'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="adm-form-footer">
            <button type="button" className="adm-btn adm-btn-ghost" onClick={onClose}>Batal</button>
            <button type="submit" className="adm-btn adm-btn-primary" disabled={saving}>
              {saving ? 'Menyimpan...' : Gigs ? 'Simpan Perubahan' : 'Tambah Gigs'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Artists Panel ────────────────────────────────────────────────────────────
function ArtistsPanel({ showToast }) {
  const [artists, setArtists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [editArtist, setEditArtist] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [genres, setGenres] = useState([]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      const data = await fetchAdminArtists(params);
      setArtists(data.results || data);
    } catch (e) {
      showToast(e.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
  }, [load]);

  useEffect(() => {
    fetchAdminGenres().then(d => setGenres(d.results || d)).catch(() => { });
  }, []);

  const handleDelete = async (id) => {
    try {
      await deleteAdminArtist(id);
      showToast('Artis berhasil dihapus.', 'success');
      load();
    } catch (e) {
      showToast(e.message, 'error');
    }
    setConfirmDelete(null);
  };

  return (
    <div className="adm-panel">
      {confirmDelete && (
        <ConfirmDialog
          message={`Hapus artis "${confirmDelete.name}"?`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}

      <div className="adm-panel-header">
        <div className="adm-panel-search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
          <input placeholder="Cari artis atau band..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <button className="adm-btn adm-btn-primary" onClick={() => { setEditArtist(null); setShowForm(true); }}>
          + Tambah Artis
        </button>
      </div>

      {showForm && (
        <ArtistForm
          artist={editArtist}
          genres={genres}
          onClose={() => { setShowForm(false); setEditArtist(null); }}
          onSaved={() => { setShowForm(false); setEditArtist(null); load(); showToast('Artis berhasil disimpan!', 'success'); }}
          showToast={showToast}
        />
      )}

      {loading ? (
        <div className="adm-loading">Memuat data artis...</div>
      ) : (
        <div className="adm-cards-grid">
          {artists.length === 0 ? (
            <div className="adm-empty">Tidak ada artis ditemukan.</div>
          ) : artists.map(artist => (
            <div key={artist.id} className="adm-artist-card">
              <div className="adm-artist-img-wrap">
                <img src={artist.display_image} alt={artist.name} />
                <div className={`adm-artist-status ${artist.is_active ? 'active' : 'inactive'}`} />
              </div>
              <div className="adm-artist-info">
                <div className="adm-artist-name">{artist.name}</div>
                <div className="adm-artist-hometown">{artist.hometown || '—'}</div>
                <div className="adm-artist-genres">
                  {artist.genres_detail?.map(g => (
                    <span key={g.id} className="adm-genre-chip" style={{ background: g.color + '33', color: g.color, borderColor: g.color + '66' }}>{g.name}</span>
                  ))}
                </div>
                <div className="adm-artist-meta">{artist.Gigs_count} Gigs</div>
              </div>
              <div className="adm-artist-actions">
                <button className="adm-btn-icon adm-btn-edit" onClick={() => { setEditArtist(artist); setShowForm(true); }}>✏️</button>
                <button className="adm-btn-icon adm-btn-del" onClick={() => setConfirmDelete(artist)}>🗑️</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ArtistForm({ artist, genres, onClose, onSaved, showToast }) {
  const [form, setForm] = useState({
    name: artist?.name || '',
    bio: artist?.bio || '',
    hometown: artist?.hometown || '',
    instagram_url: artist?.instagram_url || '',
    spotify_url: artist?.spotify_url || '',
    image_url: artist?.image_url || '',
    is_active: artist?.is_active !== undefined ? artist.is_active : true,
    genres: artist?.genres || [],
  });
  const [saving, setSaving] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const toggleGenre = (genreId) => {
    setForm(prev => ({
      ...prev,
      genres: prev.genres.includes(genreId)
        ? prev.genres.filter(g => g !== genreId)
        : [...prev.genres, genreId]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (artist) {
        await updateAdminArtist(artist.id, form);
      } else {
        await createAdminArtist(form);
      }
      onSaved();
    } catch (err) {
      showToast('Gagal menyimpan: ' + err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="adm-form-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="adm-form-panel">
        <div className="adm-form-header">
          <h2>{artist ? '✏️ Edit Artis' : '➕ Tambah Artis Baru'}</h2>
          <button className="adm-form-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="adm-form">
          <div className="adm-form-grid">
            <div className="adm-form-field adm-span-2">
              <label>Nama Artis / Band *</label>
              <input name="name" value={form.name} onChange={handleChange} required placeholder="Nama artis..." />
            </div>
            <div className="adm-form-field">
              <label>Kota Asal</label>
              <input name="hometown" value={form.hometown} onChange={handleChange} placeholder="Jakarta, Bandung, ..." />
            </div>
            <div className="adm-form-field">
              <label>URL Foto Artis</label>
              <input name="image_url" value={form.image_url} onChange={handleChange} placeholder="https://..." />
            </div>
            <div className="adm-form-field">
              <label>Instagram</label>
              <input name="instagram_url" value={form.instagram_url} onChange={handleChange} placeholder="https://instagram.com/..." />
            </div>
            <div className="adm-form-field">
              <label>Spotify</label>
              <input name="spotify_url" value={form.spotify_url} onChange={handleChange} placeholder="https://open.spotify.com/..." />
            </div>
            <div className="adm-form-field adm-span-2">
              <label>Biografi Singkat</label>
              <textarea name="bio" value={form.bio} onChange={handleChange} rows="3" placeholder="Tentang artis..." />
            </div>
            <div className="adm-form-field adm-span-2">
              <label>Genre Musik</label>
              <div className="adm-genre-picker">
                {genres.map(g => (
                  <button type="button" key={g.id}
                    className={`adm-genre-chip ${form.genres.includes(g.id) ? 'selected' : ''}`}
                    style={form.genres.includes(g.id) ? { background: g.color, color: '#fff', borderColor: g.color } : { borderColor: g.color + '66', color: g.color }}
                    onClick={() => toggleGenre(g.id)}>
                    {g.name}
                  </button>
                ))}
              </div>
            </div>
            <div className="adm-form-field adm-checkboxes">
              <label className="adm-checkbox-label">
                <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} />
                Artis Aktif
              </label>
            </div>
          </div>
          <div className="adm-form-footer">
            <button type="button" className="adm-btn adm-btn-ghost" onClick={onClose}>Batal</button>
            <button type="submit" className="adm-btn adm-btn-primary" disabled={saving}>
              {saving ? 'Menyimpan...' : artist ? 'Simpan Perubahan' : 'Tambah Artis'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Venues Panel ─────────────────────────────────────────────────────────────
function VenuesPanel({ showToast }) {
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [editVenue, setEditVenue] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      const data = await fetchAdminVenues(params);
      setVenues(data.results || data);
    } catch (e) {
      showToast(e.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
  }, [load]);

  const handleDelete = async (id) => {
    try {
      await deleteAdminVenue(id);
      showToast('Venue berhasil dihapus.', 'success');
      load();
    } catch (e) {
      showToast(e.message, 'error');
    }
    setConfirmDelete(null);
  };

  return (
    <div className="adm-panel">
      {confirmDelete && (
        <ConfirmDialog
          message={`Hapus venue "${confirmDelete.name}"?`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}

      <div className="adm-panel-header">
        <div className="adm-panel-search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
          <input placeholder="Cari venue atau kota..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <button className="adm-btn adm-btn-primary" onClick={() => { setEditVenue(null); setShowForm(true); }}>
          + Tambah Venue
        </button>
      </div>

      {showForm && (
        <VenueForm
          venue={editVenue}
          onClose={() => { setShowForm(false); setEditVenue(null); }}
          onSaved={() => { setShowForm(false); setEditVenue(null); load(); showToast('Venue berhasil disimpan!', 'success'); }}
          showToast={showToast}
        />
      )}

      {loading ? (
        <div className="adm-loading">Memuat data venue...</div>
      ) : (
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead>
              <tr><th>Foto</th><th>Nama Venue</th><th>Kota</th><th>Kapasitas</th><th>Status</th><th>Aksi</th></tr>
            </thead>
            <tbody>
              {venues.length === 0 ? (
                <tr><td colSpan={6} className="adm-empty">Tidak ada venue ditemukan.</td></tr>
              ) : venues.map(venue => (
                <tr key={venue.id}>
                  <td><img src={venue.display_image} alt={venue.name} className="adm-table-poster" /></td>
                  <td>
                    <div className="adm-table-name">{venue.name}</div>
                    <div className="adm-table-city">{venue.address?.slice(0, 40)}...</div>
                  </td>
                  <td>{venue.city}, {venue.province}</td>
                  <td>{venue.capacity ? venue.capacity.toLocaleString('id-ID') : '—'}</td>
                  <td>
                    <span className={`adm-status-badge ${venue.is_active ? '' : 'inactive'}`}
                      style={{ background: venue.is_active ? '#00e676' : '#9e9e9e' }}>
                      {venue.is_active ? 'Aktif' : 'Non-aktif'}
                    </span>
                  </td>
                  <td>
                    <div className="adm-actions">
                      <button className="adm-btn-icon adm-btn-edit" onClick={() => { setEditVenue(venue); setShowForm(true); }}>✏️</button>
                      <button className="adm-btn-icon adm-btn-del" onClick={() => setConfirmDelete(venue)}>🗑️</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function VenueForm({ venue, onClose, onSaved, showToast }) {
  const [form, setForm] = useState({
    name: venue?.name || '',
    address: venue?.address || '',
    city: venue?.city || 'Jakarta',
    province: venue?.province || 'DKI Jakarta',
    capacity: venue?.capacity || '',
    maps_url: venue?.maps_url || '',
    instagram_url: venue?.instagram_url || '',
    image_url: venue?.image_url || '',
    is_active: venue?.is_active !== undefined ? venue.is_active : true,
  });
  const [saving, setSaving] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (venue) {
        await updateAdminVenue(venue.id, form);
      } else {
        await createAdminVenue(form);
      }
      onSaved();
    } catch (err) {
      showToast('Gagal menyimpan: ' + err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="adm-form-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="adm-form-panel">
        <div className="adm-form-header">
          <h2>{venue ? '✏️ Edit Venue' : '➕ Tambah Venue Baru'}</h2>
          <button className="adm-form-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="adm-form">
          <div className="adm-form-grid">
            <div className="adm-form-field adm-span-2">
              <label>Nama Venue *</label>
              <input name="name" value={form.name} onChange={handleChange} required placeholder="Nama venue..." />
            </div>
            <div className="adm-form-field">
              <label>Kota *</label>
              <input name="city" value={form.city} onChange={handleChange} required placeholder="Jakarta" />
            </div>
            <div className="adm-form-field">
              <label>Provinsi</label>
              <input name="province" value={form.province} onChange={handleChange} placeholder="DKI Jakarta" />
            </div>
            <div className="adm-form-field adm-span-2">
              <label>Alamat Lengkap *</label>
              <textarea name="address" value={form.address} onChange={handleChange} required rows="2" placeholder="Alamat lengkap venue..." />
            </div>
            <div className="adm-form-field">
              <label>Kapasitas</label>
              <input type="number" name="capacity" value={form.capacity} onChange={handleChange} placeholder="5000" />
            </div>
            <div className="adm-form-field">
              <label>URL Foto Venue</label>
              <input name="image_url" value={form.image_url} onChange={handleChange} placeholder="https://..." />
            </div>
            <div className="adm-form-field">
              <label>Google Maps URL</label>
              <input name="maps_url" value={form.maps_url} onChange={handleChange} placeholder="https://maps.google.com/..." />
            </div>
            <div className="adm-form-field">
              <label>Instagram Venue</label>
              <input name="instagram_url" value={form.instagram_url} onChange={handleChange} placeholder="https://instagram.com/..." />
            </div>
            <div className="adm-form-field adm-checkboxes">
              <label className="adm-checkbox-label">
                <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} />
                Venue Aktif
              </label>
            </div>
          </div>
          <div className="adm-form-footer">
            <button type="button" className="adm-btn adm-btn-ghost" onClick={onClose}>Batal</button>
            <button type="submit" className="adm-btn adm-btn-primary" disabled={saving}>
              {saving ? 'Menyimpan...' : venue ? 'Simpan Perubahan' : 'Tambah Venue'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Genres Panel ─────────────────────────────────────────────────────────────
function GenresPanel({ showToast }) {
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editGenre, setEditGenre] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAdminGenres();
      setGenres(data.results || data);
    } catch (e) {
      showToast(e.message, 'error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleDelete = async (id) => {
    try {
      await deleteAdminGenre(id);
      showToast('Genre berhasil dihapus.', 'success');
      load();
    } catch (e) {
      showToast(e.message, 'error');
    }
    setConfirmDelete(null);
  };

  const handleSaveGenre = async (data) => {
    try {
      if (editGenre) {
        await updateAdminGenre(editGenre.id, data);
      } else {
        await createAdminGenre(data);
      }
      showToast('Genre berhasil disimpan!', 'success');
      load();
      setShowForm(false);
      setEditGenre(null);
    } catch (e) {
      showToast(e.message, 'error');
    }
  };

  return (
    <div className="adm-panel">
      {confirmDelete && (
        <ConfirmDialog
          message={`Hapus genre "${confirmDelete.name}"?`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}
      <div className="adm-panel-header">
        <h3 style={{ color: 'var(--text-primary)', fontSize: '1rem' }}>Kelola Genre Musik</h3>
        <button className="adm-btn adm-btn-primary" onClick={() => { setEditGenre(null); setShowForm(true); }}>
          + Tambah Genre
        </button>
      </div>

      {showForm && (
        <GenreForm
          genre={editGenre}
          onClose={() => { setShowForm(false); setEditGenre(null); }}
          onSave={handleSaveGenre}
        />
      )}

      {loading ? <div className="adm-loading">Memuat genre...</div> : (
        <div className="adm-genre-grid">
          {genres.map(genre => (
            <div key={genre.id} className="adm-genre-card" style={{ borderColor: genre.color + '66' }}>
              <div className="adm-genre-color" style={{ background: genre.color }} />
              <div className="adm-genre-name" style={{ color: genre.color }}>{genre.name}</div>
              <div className="adm-genre-count">{genre.artists_count} artis</div>
              <div className="adm-genre-slug">{genre.slug}</div>
              <div className="adm-genre-card-actions">
                <button className="adm-btn-icon adm-btn-edit" onClick={() => { setEditGenre(genre); setShowForm(true); }}>✏️</button>
                <button className="adm-btn-icon adm-btn-del" onClick={() => setConfirmDelete(genre)}>🗑️</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function GenreForm({ genre, onClose, onSave }) {
  const [name, setName] = useState(genre?.name || '');
  const [color, setColor] = useState(genre?.color || '#FF3366');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    await onSave({ name, color });
    setSaving(false);
  };

  return (
    <div className="adm-form-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="adm-form-panel" style={{ maxWidth: '420px' }}>
        <div className="adm-form-header">
          <h2>{genre ? '✏️ Edit Genre' : '➕ Tambah Genre'}</h2>
          <button className="adm-form-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="adm-form">
          <div className="adm-form-grid">
            <div className="adm-form-field adm-span-2">
              <label>Nama Genre *</label>
              <input value={name} onChange={e => setName(e.target.value)} required placeholder="Indie Rock, Jazz, Pop, ..." />
            </div>
            <div className="adm-form-field">
              <label>Warna Badge</label>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <input type="color" value={color} onChange={e => setColor(e.target.value)} style={{ width: 44, height: 44, padding: 2, borderRadius: 8, border: 'none', background: 'transparent', cursor: 'pointer' }} />
                <span className="adm-genre-chip" style={{ background: color + '33', color, borderColor: color + '66' }}>{name || 'Preview'}</span>
              </div>
            </div>
          </div>
          <div className="adm-form-footer">
            <button type="button" className="adm-btn adm-btn-ghost" onClick={onClose}>Batal</button>
            <button type="submit" className="adm-btn adm-btn-primary" disabled={saving}>
              {saving ? 'Menyimpan...' : genre ? 'Simpan' : 'Tambah Genre'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Users Panel ──────────────────────────────────────────────────────────────
function UsersPanel({ showToast }) {
  const { user: currentUser, isSuperuser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [confirmDelete, setConfirmDelete] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAdminUsers();
      setUsers(data.results || data);
    } catch (e) {
      showToast(e.message, 'error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleToggleStaff = async (user) => {
    try {
      await updateAdminUser(user.id, { is_staff: !user.is_staff });
      showToast(`Status staff "${user.username}" diperbarui.`, 'success');
      load();
    } catch (e) {
      showToast(e.message, 'error');
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteAdminUser(id);
      showToast('User berhasil dihapus.', 'success');
      load();
    } catch (e) {
      showToast(e.message, 'error');
    }
    setConfirmDelete(null);
  };

  return (
    <div className="adm-panel">
      {confirmDelete && (
        <ConfirmDialog
          message={`Hapus user "${confirmDelete.username}"? Aksi ini tidak bisa dibatalkan.`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}
      <div className="adm-panel-header">
        <h3 style={{ color: 'var(--text-primary)', fontSize: '1rem' }}>Manajemen User ({users.length})</h3>
      </div>
      {loading ? <div className="adm-loading">Memuat data user...</div> : (
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Metode Login</th>
                <th>Email</th>
                <th>Login Terakhir</th>
                <th>Disimpan</th>
                <th>Role</th>
                {isSuperuser && <th>Aksi</th>}
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id} className={user.id === currentUser?.id ? 'adm-table-self' : ''}>
                  <td>
                    <div className="adm-user-info">
                      <div className="adm-user-avatar">
                        {user.auth_provider === 'google' ? '🌐' : user.auth_provider === 'guest' ? '👤' : (user.first_name || user.username)[0].toUpperCase()}
                      </div>
                      <div>
                        <div className="adm-table-name">{user.username} {user.id === currentUser?.id && <span className="adm-badge-you">Kamu</span>}</div>
                        <div className="adm-table-city">{user.first_name} {user.last_name} {user.referral_code && <code style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)' }}>({user.referral_code})</code>}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    {user.auth_provider === 'google' ? (
                      <span className="adm-status-badge" style={{ background: '#4285F4', color: '#fff' }}>🌐 Google</span>
                    ) : user.auth_provider === 'guest' ? (
                      <span className="adm-status-badge" style={{ background: '#64748B', color: '#fff' }}>👤 Guest</span>
                    ) : (
                      <span className="adm-status-badge" style={{ background: '#334155', color: '#fff' }}>✉️ Email/Pass</span>
                    )}
                  </td>
                  <td>{user.email || '—'}</td>
                  <td className="adm-table-date">
                    {user.last_login
                      ? new Date(user.last_login).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
                      : <span style={{ color: 'var(--text-muted)' }}>Belum Pernah</span>}
                  </td>
                  <td>
                    <span style={{ fontWeight: 700, color: (user.saved_gigs_count > 0 ? 'var(--accent-pink)' : 'var(--text-muted)') }}>
                      {user.saved_gigs_count || 0} konser
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {user.is_superuser && <span className="adm-status-badge" style={{ background: '#ff0055' }}>Superuser</span>}
                      {user.is_staff && !user.is_superuser && <span className="adm-status-badge" style={{ background: '#7928ca' }}>Staff</span>}
                      {!user.is_staff && <span className="adm-status-badge" style={{ background: '#444' }}>User</span>}
                    </div>
                  </td>
                  {isSuperuser && (
                    <td>
                      <div className="adm-actions">
                        {!user.is_superuser && user.id !== currentUser?.id && (
                          <button
                            className={`adm-btn adm-btn-sm ${user.is_staff ? 'adm-btn-ghost' : 'adm-btn-purple'}`}
                            onClick={() => handleToggleStaff(user)}
                            title={user.is_staff ? 'Cabut akses staff' : 'Jadikan staff'}
                          >
                            {user.is_staff ? '⬇ Cabut Staff' : '⬆ Jadikan Staff'}
                          </button>
                        )}
                        {user.id !== currentUser?.id && !user.is_superuser && (
                          <button className="adm-btn-icon adm-btn-del" onClick={() => setConfirmDelete(user)} title="Hapus user">🗑️</button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ─── Main AdminPanel Component ────────────────────────────────────────────────
export default function AdminPanel({ onClose }) {
  const { user, login, logout, isAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [toast, setToast] = useState(null);

  // Admin login states if not authenticated as admin
  const [adminUsername, setAdminUsername] = useState('admin');
  const [adminPassword, setAdminPassword] = useState('admin123');
  const [adminLoginLoading, setAdminLoginLoading] = useState(false);
  const [adminLoginError, setAdminLoginError] = useState('');

  useEffect(() => {
    if (isAdmin) {
      fetchAdminStats()
        .then(setStats)
        .catch(e => showToast(e.message, 'error'));
    }
  }, [isAdmin]);

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
  }, []);

  const handleLogout = async () => {
    await logout();
    if (onClose) onClose();
  };

  const handleAdminLoginSubmit = async (e) => {
    e.preventDefault();
    setAdminLoginError('');
    setAdminLoginLoading(true);
    try {
      const res = await login(adminUsername, adminPassword);
      if (!res?.user?.is_staff && !res?.user?.is_superuser) {
        setAdminLoginError('Akun ini bukan administrator atau staff.');
      } else {
        showToast('Berhasil masuk ke Admin Panel!', 'success');
      }
    } catch (err) {
      setAdminLoginError(err.message || 'Login admin gagal');
    } finally {
      setAdminLoginLoading(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="adm-overlay" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="adm-access-denied" style={{ maxWidth: '440px', padding: '36px 30px', textAlign: 'center', background: '#12131C', borderRadius: '18px', border: '1px solid rgba(255,255,255,0.12)', boxShadow: '0 20px 50px rgba(0,0,0,0.6)' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>🔐</div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '6px', color: '#fff' }}>Login Admin Panel</h2>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginBottom: '22px' }}>
            Masuk sebagai Administrator untuk mengelola konser, artis, tiket, dan memantau status login pengguna.
          </p>

          <form onSubmit={handleAdminLoginSubmit} style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Username Admin</label>
              <input
                type="text"
                value={adminUsername}
                onChange={e => setAdminUsername(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', fontSize: '0.9rem' }}
                placeholder="admin"
                required
              />
            </div>
            <div>
              <label style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Password</label>
              <input
                type="password"
                value={adminPassword}
                onChange={e => setAdminPassword(e.target.value)}
                style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', fontSize: '0.9rem' }}
                placeholder="admin123"
                required
              />
            </div>

            {adminLoginError && (
              <div style={{ color: '#FF1744', fontSize: '0.82rem', background: 'rgba(255,23,68,0.1)', padding: '8px 12px', borderRadius: '6px' }}>
                {adminLoginError}
              </div>
            )}

            <button
              type="submit"
              className="adm-btn adm-btn-primary"
              style={{ width: '100%', padding: '12px', fontSize: '0.92rem', marginTop: '6px' }}
              disabled={adminLoginLoading}
            >
              {adminLoginLoading ? 'Memverifikasi...' : 'Masuk ke Admin Panel ↗'}
            </button>

            <button
              type="button"
              className="adm-btn adm-btn-ghost"
              style={{ width: '100%' }}
              onClick={onClose}
            >
              ← Kembali ke Beranda
            </button>
          </form>
        </div>
      </div>
    );
  }

  const TABS = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'Gigss', label: 'Gigs & Acara', icon: '🎸' },
    { id: 'artists', label: 'Artis', icon: '🎤' },
    { id: 'venues', label: 'Venue', icon: '🏟️' },
    { id: 'genres', label: 'Genre', icon: '🎵' },
    { id: 'users', label: 'Users', icon: '👥' },
  ];

  return (
    <div className="adm-overlay">
      <div className="adm-container">
        {/* Sidebar */}
        <aside className="adm-sidebar">
          <div className="adm-sidebar-logo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--accent-pink)" strokeWidth="2" strokeLinecap="round">
              <path d="M9 18V5l12-2v13" />
              <circle cx="6" cy="18" r="3" /><circle cx="18" cy="16" r="3" />
            </svg>
            <div>
              <div className="adm-sidebar-title">GigsSTRACK</div>
              <div className="adm-sidebar-sub">Admin Panel</div>
            </div>
          </div>

          <nav className="adm-nav">
            {TABS.map(tab => (
              <button
                key={tab.id}
                className={`adm-nav-item ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <span className="adm-nav-icon">{tab.icon}</span>
                <span>{tab.label}</span>
                {tab.id === 'dashboard' && stats && (
                  <span className="adm-nav-badge">{stats.Gigss.today}</span>
                )}
              </button>
            ))}
          </nav>

          <div className="adm-sidebar-footer">
            <div className="adm-user-chip">
              <div className="adm-user-avatar">{(user?.first_name || user?.username || 'A')[0].toUpperCase()}</div>
              <div className="adm-user-details">
                <div className="adm-user-name">{user?.first_name || user?.username}</div>
                <div className="adm-user-role">{user?.is_superuser ? 'Superuser' : 'Staff'}</div>
              </div>
            </div>
            <div className="adm-sidebar-footer-actions">
              <button className="adm-btn adm-btn-ghost adm-btn-sm" onClick={onClose}>← Kembali</button>
              <button className="adm-btn adm-btn-danger adm-btn-sm" onClick={handleLogout}>Logout</button>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="adm-main">
          <div className="adm-main-header">
            <div>
              <h1 className="adm-main-title">
                {TABS.find(t => t.id === activeTab)?.icon} {TABS.find(t => t.id === activeTab)?.label}
              </h1>
              <p className="adm-main-sub">
                {activeTab === 'dashboard' && 'Ringkasan statistik dan aktivitas terbaru GigsSTRACK.'}
                {activeTab === 'Gigss' && 'Kelola semua Gigs, konser, dan acara musik.'}
                {activeTab === 'artists' && 'Kelola daftar artis dan band yang terdaftar.'}
                {activeTab === 'venues' && 'Kelola venue dan tempat pertunjukan.'}
                {activeTab === 'genres' && 'Kelola genre dan kategori musik.'}
                {activeTab === 'users' && 'Manajemen akun dan hak akses user.'}
              </p>
            </div>
            <button className="adm-refresh-btn" onClick={() => {
              fetchAdminStats().then(setStats).catch(() => { });
            }} title="Refresh stats">↻</button>
          </div>

          <div className="adm-content">
            {activeTab === 'dashboard' && <DashboardPanel stats={stats} />}
            {activeTab === 'Gigss' && <GigssPanel showToast={showToast} />}
            {activeTab === 'artists' && <ArtistsPanel showToast={showToast} />}
            {activeTab === 'venues' && <VenuesPanel showToast={showToast} />}
            {activeTab === 'genres' && <GenresPanel showToast={showToast} />}
            {activeTab === 'users' && <UsersPanel showToast={showToast} />}
          </div>
        </main>
      </div>

      {toast && (
        <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
      )}
    </div>
  );
}
