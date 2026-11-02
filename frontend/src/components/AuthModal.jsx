import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';

function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return {};
  }
}

export default function AuthModal({ onClose }) {
  const { loginGoogle, loading } = useAuth();
  const [googlePrompt, setGooglePrompt] = useState(false);
  const [googleEmail, setGoogleEmail] = useState('');
  const [googleName, setGoogleName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const googleBtnContainerRef = useRef(null);

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  // Load Google Identity Services (GIS) if client id configured
  useEffect(() => {
    if (!googleClientId) return;

    let script = document.getElementById('google-gsi-client');
    if (!script) {
      script = document.createElement('script');
      script.id = 'google-gsi-client';
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      document.body.appendChild(script);
    }

    const initGoogleGsi = () => {
      if (window.google?.accounts?.id) {
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: async (response) => {
            if (response && response.credential) {
              setError('');
              try {
                const payload = parseJwt(response.credential);
                await loginGoogle({
                  credential: response.credential,
                  email: payload.email,
                  name: payload.name,
                  avatar_url: payload.picture,
                  google_id: payload.sub,
                });
                setSuccess(`Halo, ${payload.name || 'Pengguna Google'}! Berhasil login.`);
                setTimeout(() => onClose(), 800);
              } catch (err) {
                setError(err.message || 'Gagal login dengan Google');
              }
            }
          },
        });

        if (googleBtnContainerRef.current) {
          window.google.accounts.id.renderButton(googleBtnContainerRef.current, {
            theme: 'outline',
            size: 'large',
            width: 320,
            text: 'continue_with',
            shape: 'pill',
          });
        }
      }
    };

    if (window.google?.accounts?.id) {
      initGoogleGsi();
    } else if (script) {
      script.onload = initGoogleGsi;
    }
  }, [googleClientId, loginGoogle, onClose]);

  const handleGoogleSubmit = async (e) => {
    if (e) e.preventDefault();
    setError('');
    try {
      const emailToUse = (googleEmail || '').trim() || 'penonton.musik@gmail.com';
      const nameToUse = (googleName || '').trim() || 'Penonton Musik';
      const data = await loginGoogle({
        email: emailToUse,
        name: nameToUse,
      });
      setSuccess(`Berhasil masuk sebagai ${data.user?.first_name || nameToUse}!`);
      setTimeout(() => onClose(), 800);
    } catch (err) {
      setError(err.message || 'Gagal Login Google');
    }
  };

  const handleNativeOrPromptClick = () => {
    // If real Google GSI is available and client ID is set, trigger prompt
    if (googleClientId && window.google?.accounts?.id) {
      try {
        window.google.accounts.id.prompt();
        return;
      } catch {
        // Fallback to prompt form
      }
    }
    setGooglePrompt(true);
  };

  return (
    <div className="auth-modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="auth-modal" style={{ maxWidth: '420px', padding: '34px 28px' }}>
        <button className="auth-modal-close" onClick={onClose} aria-label="Tutup">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        <div className="auth-modal-logo" style={{ marginBottom: '14px' }}>
          <span className="dot-live"></span>
          <span>GIGS<span style={{ color: 'var(--accent-pink)' }}>TRACK</span></span>
        </div>

        <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff', marginBottom: '8px', textAlign: 'center' }}>
          Simpan Konser Favoritmu
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'center', lineHeight: 1.55, marginBottom: '22px' }}>
          Tautkan akun Google untuk menyimpan jadwal gigs, festival, dan sinkronisasi agenda musikmu di perangkat manapun.
        </p>

        {error && <div className="auth-error" style={{ marginBottom: '14px' }}>{error}</div>}
        {success && <div className="auth-success" style={{ marginBottom: '14px' }}>{success}</div>}

        {/* Real Google GSI Render Container if configured */}
        {googleClientId && (
          <div
            ref={googleBtnContainerRef}
            style={{ display: 'flex', justifyContent: 'center', marginBottom: '12px' }}
          />
        )}

        {/* 1-Click Google Login Button / Form */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {googlePrompt ? (
            <form onSubmit={handleGoogleSubmit} className="google-prompt-form" style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '14px', border: '1px solid rgba(255,255,255,0.1)' }}>
              <div style={{ fontSize: '0.86rem', fontWeight: 700, color: '#fff', marginBottom: '10px' }}>
                Hubungkan Akun Google Kamu
              </div>
              <div className="auth-field" style={{ marginBottom: '8px' }}>
                <input
                  type="email"
                  placeholder="Alamat Gmail (contoh: kamu@gmail.com)"
                  value={googleEmail}
                  onChange={(e) => setGoogleEmail(e.target.value)}
                  autoFocus
                  required
                />
              </div>
              <div className="auth-field" style={{ marginBottom: '12px' }}>
                <input
                  type="text"
                  placeholder="Nama Lengkap (opsional)"
                  value={googleName}
                  onChange={(e) => setGoogleName(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button type="button" className="btn-secondary" onClick={() => setGooglePrompt(false)} style={{ flex: 1, padding: '9px' }}>
                  Batal
                </button>
                <button type="submit" className="btn-primary" disabled={loading} style={{ flex: 2, padding: '9px' }}>
                  {loading ? 'Menghubungkan...' : 'Lanjutkan'}
                </button>
              </div>
            </form>
          ) : (
            <button
              type="button"
              className="btn-social-login btn-google"
              onClick={handleNativeOrPromptClick}
              disabled={loading}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px',
                padding: '13px 20px',
                borderRadius: '12px',
                background: '#ffffff',
                color: '#1f1f1f',
                fontWeight: 600,
                fontSize: '0.94rem',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: '0 4px 14px rgba(0,0,0,0.25)'
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
              </svg>
              <span>{loading ? 'Menghubungkan...' : 'Lanjutkan dengan Google'}</span>
            </button>
          )}
        </div>

        <div style={{ marginTop: '22px', textAlign: 'center', fontSize: '0.76rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
          Gratis, aman, dan instan tanpa perlu repot membuat kata sandi baru.
        </div>
      </div>
    </div>
  );
}
