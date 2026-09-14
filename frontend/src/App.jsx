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
        // Client side filtering for 'weekend' if selected
        if (dateFilter === 'weekend') {
          results = results.filter((gig) => {
            const gigDate = new Date(gig.start_datetime);
            const dayOfWeek = gigDate.getDay(); // 0 is Sunday, 5 is Friday, 6 is Saturday
            return dayOfWeek === 5 || dayOfWeek === 6 || dayOfWeek === 0;
          });
        }
        setGigs(results);
      })
      .catch((err) => {
        console.error(err);
        setGigs([]);
      })
      .finally(() => setLoading(false));
  }, [search, selectedCity, selectedGenre, dateFilter, isFreeOnly, getDateQueryParam]);

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
      />

      {/* Main Gigs Listing */}
      <main className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>
            {dateFilter === 'today' ? '🔥 Konser & Gigs Hari Ini' : '🎸 Eksplorasi Jadwal Gigs'}
          </h2>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Menampilkan {gigs.length} acara
          </span>
        </div>

        {loading ? (
          <div style={{ padding: '80px 20px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <div style={{ fontSize: '1.4rem', marginBottom: '10px' }}>⚡ Menghubungkan ke radar konser...</div>
          </div>
        ) : gigs.length > 0 ? (
          <div className="gigs-grid">
            {gigs.map((gig) => (
              <GigCard
                key={gig.id}
                gig={gig}
                onSelect={(selected) => setSelectedGigId(selected.id)}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">🎸</div>
            <h3>Tidak Ada Gig Ditemukan</h3>
            <p>
              Coba reset filter kota atau ubah kata kunci pencarian untuk menemukan konser musik lainnya.
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
        />
      )}

      <Footer />
    </div>
  );
}
