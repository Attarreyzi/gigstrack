const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

export async function fetchTodayGigs() {
  const res = await fetch(`${API_BASE_URL}/gigs/today/`);
  if (!res.ok) throw new Error('Gagal mengambil data gig hari ini');
  return res.json();
}

export async function fetchGigs(params = {}) {
  const query = new URLSearchParams();
  if (params.search) query.append('search', params.search);
  if (params.city) query.append('city', params.city);
  if (params.genre) query.append('genre', params.genre);
  if (params.date) query.append('date', params.date);
  if (params.is_free !== undefined && params.is_free !== '') query.append('is_free', params.is_free);

  const res = await fetch(`${API_BASE_URL}/gigs/?${query.toString()}`);
  if (!res.ok) throw new Error('Gagal mengambil daftar gig');
  const data = await res.json();
  return data.results || data;
}

export async function fetchGigDetail(id) {
  const res = await fetch(`${API_BASE_URL}/gigs/${id}/`);
  if (!res.ok) throw new Error('Gagal mengambil detail konser');
  return res.json();
}

export async function fetchGenres() {
  const res = await fetch(`${API_BASE_URL}/artists/genres/`);
  if (!res.ok) throw new Error('Gagal mengambil daftar genre');
  return res.json();
}

export async function fetchCities() {
  const res = await fetch(`${API_BASE_URL}/gigs/cities/`);
  if (!res.ok) throw new Error('Gagal mengambil daftar kota');
  return res.json();
}

export async function fetchStats() {
  const res = await fetch(`${API_BASE_URL}/gigs/summary_stats/`);
  if (!res.ok) throw new Error('Gagal mengambil statistik');
  return res.json();
}
