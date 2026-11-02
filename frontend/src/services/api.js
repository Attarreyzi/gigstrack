const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

// ─── Token Management ─────────────────────────────────────────────────────────

export function getAccessToken() {
  return localStorage.getItem('gt_access');
}

export function getRefreshToken() {
  return localStorage.getItem('gt_refresh');
}

export function setTokens(access, refresh) {
  localStorage.setItem('gt_access', access);
  if (refresh) localStorage.setItem('gt_refresh', refresh);
}

export function clearTokens() {
  localStorage.removeItem('gt_access');
  localStorage.removeItem('gt_refresh');
  localStorage.removeItem('gt_user');
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem('gt_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setStoredUser(user) {
  localStorage.setItem('gt_user', JSON.stringify(user));
}

// ─── Authenticated Fetch ──────────────────────────────────────────────────────

async function authFetch(url, options = {}) {
  const access = getAccessToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (access) headers['Authorization'] = `Bearer ${access}`;

  // Don't set Content-Type for FormData
  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
  }

  const res = await fetch(url, { ...options, headers });

  // Try to refresh token if 401
  if (res.status === 401) {
    const refresh = getRefreshToken();
    if (refresh) {
      const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (refreshRes.ok) {
        const data = await refreshRes.json();
        setTokens(data.access, data.refresh);
        headers['Authorization'] = `Bearer ${data.access}`;
        return fetch(url, { ...options, headers });
      } else {
        clearTokens();
        window.dispatchEvent(new Event('auth:logout'));
        throw new Error('Session habis, silakan login kembali.');
      }
    }
  }

  return res;
}

// ─── Auth API ─────────────────────────────────────────────────────────────────

export async function loginUser(username, password) {
  const res = await fetch(`${API_BASE_URL}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.non_field_errors?.[0] || 'Login gagal');
  }
  const data = await res.json();
  setTokens(data.access, data.refresh);
  setStoredUser(data.user);
  return data;
}

export async function registerUser(payload) {
  const res = await fetch(`${API_BASE_URL}/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const msg = Object.values(err).flat().join(' ') || 'Registrasi gagal';
    throw new Error(msg);
  }
  const data = await res.json();
  setTokens(data.access, data.refresh);
  setStoredUser(data.user);
  return data;
}

export async function logoutUser() {
  const refresh = getRefreshToken();
  try {
    await authFetch(`${API_BASE_URL}/auth/logout/`, {
      method: 'POST',
      body: JSON.stringify({ refresh }),
    });
  } catch {
    // ignore
  }
  clearTokens();
}

export async function loginGoogle(payload) {
  const res = await fetch(`${API_BASE_URL}/auth/google/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload || {}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || 'Login dengan Google gagal');
  }
  const data = await res.json();
  setTokens(data.access, data.refresh);
  setStoredUser(data.user);
  return data;
}

export async function loginGuest() {
  const res = await fetch(`${API_BASE_URL}/auth/guest/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || 'Gagal masuk sebagai Tamu');
  }
  const data = await res.json();
  setTokens(data.access, data.refresh);
  setStoredUser(data.user);
  return data;
}

export async function fetchUserProfile() {
  const res = await authFetch(`${API_BASE_URL}/auth/profile/`);
  if (!res.ok) throw new Error('Gagal mengambil profil user');
  return res.json();
}

// ─── Admin API ────────────────────────────────────────────────────────────────

export async function fetchAdminStats() {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/stats/`);
  if (!res.ok) throw new Error('Gagal mengambil statistik admin');
  return res.json();
}

// Admin Users
export async function fetchAdminUsers() {
  const res = await authFetch(`${API_BASE_URL}/auth/admin/users/`);
  if (!res.ok) throw new Error('Gagal mengambil daftar user');
  return res.json();
}

export async function updateAdminUser(userId, data) {
  const res = await authFetch(`${API_BASE_URL}/auth/admin/users/${userId}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Gagal update user');
  return res.json();
}

export async function deleteAdminUser(userId) {
  const res = await authFetch(`${API_BASE_URL}/auth/admin/users/${userId}/`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Gagal menghapus user');
  return res.json();
}

// Admin Gigss CRUD
export async function fetchAdminGigss(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await authFetch(`${API_BASE_URL}/admin-panel/Gigss/?${query}`);
  if (!res.ok) throw new Error('Gagal mengambil daftar Gigs');
  return res.json();
}

export async function createAdminGigs(data) {
  const isFormData = data instanceof FormData;
  const res = await authFetch(`${API_BASE_URL}/admin-panel/Gigss/`, {
    method: 'POST',
    body: isFormData ? data : JSON.stringify(data),
    headers: isFormData ? {} : { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(JSON.stringify(err));
  }
  return res.json();
}

export async function updateAdminGigs(id, data) {
  const isFormData = data instanceof FormData;
  const res = await authFetch(`${API_BASE_URL}/admin-panel/Gigss/${id}/`, {
    method: 'PATCH',
    body: isFormData ? data : JSON.stringify(data),
    headers: isFormData ? {} : { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(JSON.stringify(err));
  }
  return res.json();
}

export async function deleteAdminGigs(id) {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/Gigss/${id}/`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Gagal menghapus Gigs');
  return true;
}

export async function addAdminLineup(gigId, data) {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/Gigss/${gigId}/add-lineup/`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(JSON.stringify(err));
  }
  return res.json();
}

export async function removeAdminLineup(gigId, lineupId) {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/Gigss/${gigId}/remove-lineup/${lineupId}/`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Gagal menghapus lineup');
  return true;
}

// Admin Artists CRUD
export async function fetchAdminArtists(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await authFetch(`${API_BASE_URL}/admin-panel/artists/?${query}`);
  if (!res.ok) throw new Error('Gagal mengambil daftar artis');
  return res.json();
}

export async function createAdminArtist(data) {
  const isFormData = data instanceof FormData;
  const res = await authFetch(`${API_BASE_URL}/admin-panel/artists/`, {
    method: 'POST',
    body: isFormData ? data : JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(JSON.stringify(err));
  }
  return res.json();
}

export async function updateAdminArtist(id, data) {
  const isFormData = data instanceof FormData;
  const res = await authFetch(`${API_BASE_URL}/admin-panel/artists/${id}/`, {
    method: 'PATCH',
    body: isFormData ? data : JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(JSON.stringify(err));
  }
  return res.json();
}

export async function deleteAdminArtist(id) {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/artists/${id}/`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Gagal menghapus artis');
  return true;
}

// Admin Venues CRUD
export async function fetchAdminVenues(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await authFetch(`${API_BASE_URL}/admin-panel/venues/?${query}`);
  if (!res.ok) throw new Error('Gagal mengambil daftar venue');
  return res.json();
}

export async function createAdminVenue(data) {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/venues/`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(JSON.stringify(err));
  }
  return res.json();
}

export async function updateAdminVenue(id, data) {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/venues/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(JSON.stringify(err));
  }
  return res.json();
}

export async function deleteAdminVenue(id) {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/venues/${id}/`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Gagal menghapus venue');
  return true;
}

// Admin Genres CRUD
export async function fetchAdminGenres(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await authFetch(`${API_BASE_URL}/admin-panel/genres/?${query}`);
  if (!res.ok) throw new Error('Gagal mengambil daftar genre');
  return res.json();
}

export async function createAdminGenre(data) {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/genres/`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(JSON.stringify(err));
  }
  return res.json();
}

export async function updateAdminGenre(id, data) {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/genres/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Gagal update genre');
  return res.json();
}

export async function deleteAdminGenre(id) {
  const res = await authFetch(`${API_BASE_URL}/admin-panel/genres/${id}/`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Gagal menghapus genre');
  return true;
}

// ─── Public API ───────────────────────────────────────────────────────────────

export async function fetchTodayGigs() {
  const res = await fetch(`${API_BASE_URL}/gigs/today/`);
  if (!res.ok) throw new Error('Gagal mengambil data Gigs HARI INI');
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

export const fetchGigsDetail = fetchGigDetail;
export const fetchGig = fetchGigs;

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

export async function fetchSavedGigs() {
  const res = await authFetch(`${API_BASE_URL}/auth/saved-gigs/`);
  if (!res.ok) throw new Error('Gagal mengambil konser tersimpan');
  return res.json();
}

export async function toggleSaveGig(gigId) {
  const res = await authFetch(`${API_BASE_URL}/auth/saved-gigs/`, {
    method: 'POST',
    body: JSON.stringify({ gig_id: gigId }),
  });
  if (!res.ok) throw new Error('Gagal memperbarui status simpan konser');
  return res.json();
}

export async function fetchPublicArtists(params = {}) {
  const query = new URLSearchParams();
  if (params.search) query.append('search', params.search);
  if (params.ordering) query.append('ordering', params.ordering);

  const res = await fetch(`${API_BASE_URL}/artists/?${query.toString()}`);
  if (!res.ok) throw new Error('Gagal mengambil daftar artis');
  const data = await res.json();
  return data.results || data;
}

