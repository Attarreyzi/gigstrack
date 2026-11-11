import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Navbar from './components/Navbar';
import TodayRadar from './components/TodayRadar';
import FilterBar from './components/FilterBar';
import GigCard from './components/GigCard';
import GigModal from './components/GigModal';
import ArtistsCatalog from './components/ArtistsCatalog';
import AboutPage from './components/AboutPage';
import ContactPage from './components/ContactPage';
import AuthModal from './components/AuthModal';
import Footer from './components/Footer';
import { useAuth } from './contexts/AuthContext';
import { fetchTodayGigs, fetchGigs, fetchGenres, fetchCities, fetchStats } from './services/api';

export default function App() {
  const { savedGigIds, savedCount, isAuthenticated, isAdmin } = useAuth();

  // Navigation tab: 'gigs' | 'artists' | 'saved' | 'about' | 'contact'
  const [activeTab, setActiveTab] = useState('gigs');

  // Modal UI state
  const [selectedGigId, setSelectedGigId] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Data states
  const [todayData, setTodayData] = useState(null);
  const [stats, setStats] = useState(null);
  const [genres, setGenres] = useState([]);
  const [cities, setCities] = useState([]);
  const [gigs, setGigs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [isSearchVisible, setIsSearchVisible] = useState(false);
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [dateFilter, setDateFilter] = useState('all');
  const [isFreeOnly, setIsFreeOnly] = useState(false);

  // Load initial today's radar data & metadata
  useEffect(() => {
    Promise.all([
      fetchTodayGigs().catch(() => null),
      fetchStats().catch(() => null),
      fetchGenres().catch(() => []),
      fetchCities().catch(() => [])
    ]).then(([todayRes, statsRes, genresRes, citiesRes]) => {
      if (todayRes) setTodayData(todayRes);
      if (statsRes) setStats(statsRes);
      if (genresRes) setGenres(genresRes);
      if (citiesRes) setCities(citiesRes);
    });
  }, []);

  // Helper date query mapping
  const getDateQueryParam = useCallback(() => {
    if (dateFilter === 'today') return 'today';
    if (dateFilter === 'tomorrow') return 'tomorrow';
    if (dateFilter === 'this_week') return 'this_week';
    if (dateFilter === 'weekend') return 'weekend';
    if (dateFilter === 'all') return 'all';
    return '';
  }, [dateFilter]);

  // Main fetch gigs with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true);

      const params = {};
      if (search) params.search = search;
      if (selectedCity) params.city = selectedCity;
      if (selectedGenre) params.genre = selectedGenre;
      if (isFreeOnly) params.is_free = 'true';

      const dateQuery = getDateQueryParam();
      if (dateQuery) params.date = dateQuery;

      fetchGigs(params)
        .then((data) => {
          setGigs(data.results || data);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Gagal memuat daftar konser:", err);
          setGigs([]);
          setLoading(false);
        });
    }, 250);

    return () => clearTimeout(timer);
  }, [search, selectedCity, selectedGenre, dateFilter, isFreeOnly, getDateQueryParam]);

  // Filtered gigs for 'saved' view
  const displayedGigs = useMemo(() => {
    if (activeTab === 'saved' || dateFilter === 'saved') {
      return gigs.filter((gig) => savedGigIds.includes(gig.id));
    }
    return gigs;
  }, [gigs, savedGigIds, activeTab, dateFilter]);

  const handleSelectArtistFromCatalog = (artistName) => {
    setSearch(artistName);
    setIsSearchVisible(true);
    setActiveTab('gigs');
    setDateFilter('all');
    setTimeout(() => {
      const el = document.getElementById('main-gigs-search-input');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.focus();
      }
    }, 120);
  };

  const handleToggleSearch = useCallback(() => {
    if (activeTab !== 'gigs') {
      setActiveTab('gigs');
    }
    setIsSearchVisible((prev) => {
      const next = !prev;
      if (next) {
        setTimeout(() => {
          const el = document.getElementById('main-gigs-search-input');
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.focus();
          }
        }, 120);
      }
      return next;
    });
  }, [activeTab]);

  const handleDateFilterFromHero = (filterKey) => {
    setActiveTab('gigs');
    setDateFilter(filterKey);
  };

  const handleNavigateFromDrawer = (menuKey) => {
    if (menuKey === 'gigs') {
      setActiveTab('gigs');
      setDateFilter('all');
      setTimeout(() => {
        const el = document.getElementById('gigs-listing-section');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 80);
    } else if (menuKey === 'today') {
      setActiveTab('gigs');
      setDateFilter('today');
      setTimeout(() => {
        const el = document.getElementById('gigs-listing-section');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 80);
    } else if (menuKey === 'artists') {
      setActiveTab('gigs');
      setTimeout(() => {
        const el = document.getElementById('artists-section');
        if (el) {
          el.scrollIntoView({ behavior: 'smooth' });
        } else {
          setActiveTab('artists');
        }
      }, 100);
    } else if (menuKey === 'about') {
      setActiveTab('about');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (menuKey === 'contact') {
      setActiveTab('contact');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (menuKey === 'venues') {
      setActiveTab('gigs');
      setDateFilter('all');
      setTimeout(() => {
        const el = document.querySelector('.city-select');
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          el.focus();
        }
      }, 100);
    } else if (menuKey === 'saved') {
      setActiveTab('saved');
      setTimeout(() => {
        const el = document.getElementById('gigs-listing-section');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 80);
    }
  };

  return (
    <div className="app-layout">
      <Navbar
        liveCount={todayData?.total_gigs_today || 0}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNavigate={handleNavigateFromDrawer}
        onOpenAuth={() => setShowAuthModal(true)}
        onToggleSearch={handleToggleSearch}
        isSearchVisible={isSearchVisible}
      />

      {/* Navigation View Switch */}
      {activeTab === 'about' ? (
        <AboutPage onNavigate={handleNavigateFromDrawer} />
      ) : activeTab === 'contact' ? (
        <ContactPage onNavigate={handleNavigateFromDrawer} />
      ) : activeTab === 'artists' ? (
        <ArtistsCatalog onSelectArtist={handleSelectArtistFromCatalog} />
      ) : (
        <>
          {/* Hero Radar Banner */}
          <TodayRadar
            todayData={todayData}
            stats={stats}
            onSelectDateFilter={handleDateFilterFromHero}
            onSelectTab={setActiveTab}
          />

          <FilterBar
            search={search}
            setSearch={setSearch}
            isSearchVisible={isSearchVisible}
            setIsSearchVisible={setIsSearchVisible}
            selectedCity={selectedCity}
            setSelectedCity={setSelectedCity}
            selectedGenre={selectedGenre}
            setSelectedGenre={setSelectedGenre}
            dateFilter={activeTab === 'saved' ? 'saved' : dateFilter}
            setDateFilter={(df) => {
              if (df === 'saved') {
                setActiveTab('saved');
              } else {
                if (activeTab === 'saved') setActiveTab('gigs');
                setDateFilter(df);
              }
            }}
            isFreeOnly={isFreeOnly}
            setIsFreeOnly={setIsFreeOnly}
            cities={cities}
            genres={genres}
            savedCount={savedCount}
          />

          {/* Main Gigs Listing */}
          <main id="gigs-listing-section" className="container">
            <div className="section-header-row">
              <h2>
                {activeTab === 'saved' || dateFilter === 'saved'
                  ? 'Konser Tersimpan'
                  : dateFilter === 'today'
                    ? 'Konser & Gigs HARI INI'
                    : dateFilter === 'this_week'
                      ? 'Konser & Gigs Minggu Ini'
                        : dateFilter === 'weekend'
                          ? 'Konser Akhir Pekan'
                          : 'Jadwal & Agenda Konser'}
              </h2>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                {displayedGigs.length} acara ditemukan
              </span>
            </div>

            {loading ? (
              <div className="gigs-loading-grid">
                {[1, 2, 3, 4, 5, 6].map((n) => (
                  <div key={n} className="skeleton-card">
                    <div className="skeleton-poster"></div>
                    <div className="skeleton-text line-1"></div>
                    <div className="skeleton-text line-2"></div>
                  </div>
                ))}
              </div>
            ) : displayedGigs.length > 0 ? (
              <div className="gigs-grid">
                {displayedGigs.map((gig) => (
                  <GigCard
                    key={gig.id}
                    gig={gig}
                    onSelect={(g) => setSelectedGigId(g.id)}
                    onRequireAuth={() => setShowAuthModal(true)}
                  />
                ))}
              </div>
            ) : (activeTab === 'saved' || dateFilter === 'saved') ? (
              <div className="radar-empty-state">
                <div style={{ color: 'var(--accent-pink)', marginBottom: '14px' }}>
                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                  </svg>
                </div>
                <h3>Belum Ada Konser Tersimpan</h3>
                <p>
                  Kamu belum menandai konser apapun. Simpan konser favoritmu agar tidak ketinggalan jadwal.
                </p>
                <button
                  type="button"
                  className="btn-primary"
                  style={{ marginTop: '20px', display: 'inline-flex' }}
                  onClick={() => {
                    setActiveTab('gigs');
                    setDateFilter('all');
                  }}
                >
                  Jelajahi Konser
                </button>
              </div>
            ) : (
              <div className="radar-empty-state">
                <div className="empty-icon"></div>
                <h3>Belum Ada Jadwal Gigs</h3>
                <p>
                  Tidak ditemukan konser musik dengan filter yang dipilih. Coba cari artis lain atau ganti kota.
                </p>
                <button
                  className="btn-secondary"
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

          {/* Katalog Band & Musisi Lokal bawaan langsung tampil terintegrasi */}
          <ArtistsCatalog onSelectArtist={handleSelectArtistFromCatalog} />
        </>
      )}

      {/* Detail Modal */}
      {selectedGigId && (
        <GigModal
          gigId={selectedGigId}
          onClose={() => setSelectedGigId(null)}
          onRequireAuth={() => setShowAuthModal(true)}
        />
      )}

      {/* Auth Modal (Google & Guest & Email) */}
      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}

      <Footer onNavigate={handleNavigateFromDrawer} />
    </div>
  );
}
