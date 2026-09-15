import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import TodayRadar from './components/TodayRadar';
import FilterBar from './components/FilterBar';
import GigCard from './components/GigCard';
import GigModal from './components/GigModal';
import Footer from './components/Footer';
import { fetchTodayGigs, fetchGigs, fetchGenres, fetchCities, fetchStats } from './services/api';

export default function App() {
  const [todayData, setTodayData] = useState(null);
  const [stats, setStats] = useState(null);
  const [genres, setGenres] = useState([]);
  const [cities, setCities] = useState([]);
  const [gigs, setGigs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [dateFilter, setDateFilter] = useState('all'); // 'all', 'today', 'tomorrow', 'weekend'
  const [isFreeOnly, setIsFreeOnly] = useState(false);

  // Modal
  const [selectedGigId, setSelectedGigId] = useState(null);

  // Bookmarks (Local Storage)
  const [bookmarks, setBookmarks] = useState(() => {
    try {
      const saved = localStorage.getItem('gigtrack_bookmarks');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const toggleBookmark = (gigId) => {
    setBookmarks((prev) => {
      const next = prev.includes(gigId)
        ? prev.filter((id) => id !== gigId)
        : [...prev, gigId];
      try {
        localStorage.setItem('gigtrack_bookmarks', JSON.stringify(next));
      } catch (e) {
        console.error(e);
      }
      return next;
    });
  };

  // Load initial today's radar data & metadata
  useEffect(() => {
    Promise.all([
      fetchTodayGigs().catch(() => null),
      fetchStats().catch(() => null),
      fetchGenres().catch(() => []),
      fetchCities().catch(() => [])
    ]).then(([todayRes, statsRes, genresRes, citiesRes]) => {
      setTodayData(todayRes);
      setStats(statsRes);
      setGenres(genresRes);
      setCities(citiesRes);
    });
  }, []);

  // Compute date string based on quick tabs
  const getDateQueryParam = useCallback(() => {
    const now = new Date();
    const formatDate = (d) => {
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };

    if (dateFilter === 'today') {
      return formatDate(now);
    } else if (dateFilter === 'tomorrow') {
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      return formatDate(tomorrow);
    }
    return '';
  }, [dateFilter]);

  // Fetch gigs whenever filters change
  useEffect(() => {
    setLoading(true);
    const dateParam = getDateQueryParam();

    fetchGigs({
      search: search.trim(),
      city: selectedCity,
      genre: selectedGenre,
      date: dateParam,
      is_free: isFreeOnly ? 'true' : ''
    })
      .then((data) => {
        let results = data;
        // Client side filtering for 'this_week' if selected
        if (dateFilter === 'this_week') {
          const now = new Date();
          const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
          const currentDay = now.getDay(); // 0 is Sunday, 1 is Monday...
          const daysUntilSunday = currentDay === 0 ? 0 : 7 - currentDay;
          const endOfWeek = new Date(now.getFullYear(), now.getMonth(), now.getDate() + daysUntilSunday, 23, 59, 59, 999);

          results = results.filter((gig) => {
            const gigDate = new Date(gig.start_datetime);
            return gigDate >= startOfToday && gigDate <= endOfWeek;
          });
        }
        // Client side filtering for 'weekend' if selected
        if (dateFilter === 'weekend') {
          results = results.filter((gig) => {
            const gigDate = new Date(gig.start_datetime);
            const dayOfWeek = gigDate.getDay(); // 0 is Sunday, 5 is Friday, 6 is Saturday
            return dayOfWeek === 5 || dayOfWeek === 6 || dayOfWeek === 0;
          });
        }
        // Client side filtering for 'saved'
        if (dateFilter === 'saved') {
          results = results.filter((gig) => bookmarks.includes(gig.id));
        }
        setGigs(results);
      })
      .catch((err) => {
        console.error(err);
        setGigs([]);
      })
      .finally(() => setLoading(false));
  }, [search, selectedCity, selectedGenre, dateFilter, isFreeOnly, bookmarks, getDateQueryParam]);

  return (
    <div className="app-layout">
      <Navbar liveCount={todayData?.total_gigs_today || 0} />

      <TodayRadar
        todayData={todayData}
        stats={stats}
        onSelectGig={(gig) => setSelectedGigId(gig.id)}
      />

      <FilterBar
        search={search}
        setSearch={setSearch}
        selectedCity={selectedCity}
        setSelectedCity={setSelectedCity}
        selectedGenre={selectedGenre}
        setSelectedGenre={setSelectedGenre}
        dateFilter={dateFilter}
        setDateFilter={setDateFilter}
        isFreeOnly={isFreeOnly}
        setIsFreeOnly={setIsFreeOnly}
        cities={cities}
        genres={genres}
        savedCount={bookmarks.length}
      />

      {/* Main Gigs Listing */}
      <main className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, letterSpacing: '-0.01em' }}>
            {dateFilter === 'today'
              ? 'Konser & Gig Hari Ini'
              : dateFilter === 'tomorrow'
                ? 'Konser & Gig Besok'
                : dateFilter === 'this_week'
                  ? 'Konser & Gig Minggu Ini'
                  : dateFilter === 'weekend'
                    ? 'Konser Akhir Pekan'
                    : dateFilter === 'saved'
                      ? 'Konser Tersimpan'
                      : 'Jadwal & Agenda Konser'}
          </h2>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
            {gigs.length} acara ditemukan
          </span>
        </div>

        {loading ? (
          <div style={{ padding: '80px 20px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <div style={{ fontSize: '1.1rem', marginBottom: '10px' }}>Memuat radar jadwal konser...</div>
          </div>
        ) : gigs.length > 0 ? (
          <div className="gigs-grid">
            {gigs.map((gig) => (
              <GigCard
                key={gig.id}
                gig={gig}
                onSelect={(selected) => setSelectedGigId(selected.id)}
                isBookmarked={bookmarks.includes(gig.id)}
                onToggleBookmark={toggleBookmark}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px', color: 'var(--text-muted)' }}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="8" y1="12" x2="16" y2="12"></line>
              </svg>
            </div>
            <h3>{dateFilter === 'saved' ? 'Belum Ada Konser Tersimpan' : 'Tidak Ada Gig Ditemukan'}</h3>
            <p>
              {dateFilter === 'saved'
                ? 'Klik ikon bookmark pada kartu konser untuk menyimpannya ke daftar agendamu.'
                : 'Coba reset filter wilayah atau ubah kata kunci pencarian untuk menemukan konser musik lainnya.'}
            </p>
            <button
              className="btn-primary"
              style={{ marginTop: '20px', display: 'inline-flex' }}
              onClick={() => {
                setSearch('');
                setSelectedCity('');
                setSelectedGenre('');
                setDateFilter('all');
                setIsFreeOnly(false);
              }}
            >
              Reset Semua Filter
            </button>
          </div>
        )}
      </main>

      {/* Detail Modal */}
      {selectedGigId && (
        <GigModal
          gigId={selectedGigId}
          onClose={() => setSelectedGigId(null)}
          isBookmarked={bookmarks.includes(selectedGigId)}
          onToggleBookmark={toggleBookmark}
        />
      )}

      <Footer />
    </div>
  );
}
