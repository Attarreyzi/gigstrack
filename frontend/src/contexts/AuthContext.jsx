import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  loginUser,
  logoutUser,
  registerUser,
  loginGoogle as apiLoginGoogle,
  loginGuest as apiLoginGuest,
  fetchUserProfile,
  fetchSavedGigs,
  toggleSaveGig,
  getStoredUser,
  getAccessToken,
  clearTokens,
  setStoredUser,
} from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser());
  const [loading, setLoading] = useState(false);
  const [savedGigIds, setSavedGigIds] = useState(() => {
    try {
      const stored = localStorage.getItem('gt_saved_gigs');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  // Load saved gigs from server if authenticated
  const refreshSaved = useCallback(async () => {
    if (!getAccessToken()) return;
    try {
      const data = await fetchSavedGigs();
      if (data && data.saved_ids) {
        setSavedGigIds(data.saved_ids);
        localStorage.setItem('gt_saved_gigs', JSON.stringify(data.saved_ids));
      }
    } catch {
      // offline / fallback
    }
  }, []);

  // Listen for forced logout (expired token)
  useEffect(() => {
    const onLogout = () => {
      setUser(null);
      setSavedGigIds([]);
    };
    window.addEventListener('auth:logout', onLogout);
    return () => window.removeEventListener('auth:logout', onLogout);
  }, []);

  // Revalidate user on mount if token exists
  useEffect(() => {
    if (getAccessToken()) {
      fetchUserProfile()
        .then((profile) => {
          setUser(profile);
          setStoredUser(profile);
          refreshSaved();
        })
        .catch(() => {
          clearTokens();
          setUser(null);
        });
    }
  }, [refreshSaved]);

  const login = useCallback(async (username, password) => {
    setLoading(true);
    try {
      const data = await loginUser(username, password);
      setUser(data.user);
      refreshSaved();
      return data;
    } finally {
      setLoading(false);
    }
  }, [refreshSaved]);

  const loginGoogle = useCallback(async (payload) => {
    setLoading(true);
    try {
      const data = await apiLoginGoogle(payload);
      setUser(data.user);
      refreshSaved();
      return data;
    } finally {
      setLoading(false);
    }
  }, [refreshSaved]);

  const loginGuest = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiLoginGuest();
      setUser(data.user);
      refreshSaved();
      return data;
    } finally {
      setLoading(false);
    }
  }, [refreshSaved]);

  const register = useCallback(async (payload) => {
    setLoading(true);
    try {
      const data = await registerUser(payload);
      setUser(data.user);
      refreshSaved();
      return data;
    } finally {
      setLoading(false);
    }
  }, [refreshSaved]);

  const logout = useCallback(async () => {
    await logoutUser();
    setUser(null);
    setSavedGigIds([]);
    localStorage.removeItem('gt_saved_gigs');
  }, []);

  const toggleSave = useCallback(async (gigId) => {
    if (!gigId) return false;

    // Optimistic UI update
    const alreadySaved = savedGigIds.includes(gigId);
    const updatedIds = alreadySaved
      ? savedGigIds.filter((id) => id !== gigId)
      : [...savedGigIds, gigId];

    setSavedGigIds(updatedIds);
    localStorage.setItem('gt_saved_gigs', JSON.stringify(updatedIds));

    if (getAccessToken()) {
      try {
        const res = await toggleSaveGig(gigId);
        if (res && res.saved_ids) {
          setSavedGigIds(res.saved_ids);
          localStorage.setItem('gt_saved_gigs', JSON.stringify(res.saved_ids));
        }
        return res?.is_saved;
      } catch (err) {
        console.error("Gagal sinkronisasi simpan konser ke server:", err);
      }
    }
    return !alreadySaved;
  }, [savedGigIds]);

  const isGigSaved = useCallback((gigId) => {
    return savedGigIds.includes(gigId);
  }, [savedGigIds]);

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.is_staff || user?.is_superuser,
    isSuperuser: user?.is_superuser,
    savedGigIds,
    savedCount: savedGigIds.length,
    login,
    loginGoogle,
    loginGuest,
    register,
    logout,
    toggleSave,
    isGigSaved,
    refreshSaved,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
