import { useState, useEffect, useRef } from 'react';

const BASE = import.meta.env.VITE_API_URL || '';

export default function BirthForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    dob: '2004-02-28',
    tob: '01:15',
    place: 'Kochi, Kerala, India',
    latitude: 9.93988,
    longitude: 76.26022,
    timezone: 'Asia/Kolkata'
  });

  const [suggestions, setSuggestions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [hasSelectedFromList, setHasSelectedFromList] = useState(true);

  const wrapperRef = useRef(null);
  const debounceTimerRef = useRef(null);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch place suggestions whenever user types
  const handlePlaceInputChange = (e) => {
    const val = e.target.value;
    setFormData((prev) => ({
      ...prev,
      place: val,
      // If user is editing text manually, clear pre-selected coordinates until a new item is picked
      latitude: null,
      longitude: null,
      timezone: null
    }));
    setHasSelectedFromList(false);
    setSelectedIndex(-1);

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    const trimmed = val.trim();
    if (trimmed.length < 2) {
      setSuggestions([]);
      setShowDropdown(false);
      setLoadingSuggestions(false);
      return;
    }

    setLoadingSuggestions(true);
    debounceTimerRef.current = setTimeout(async () => {
      try {
        // Query Open-Meteo Geocoding API directly (free, worldwide, fast, CORS-enabled)
        let results = [];
        try {
          const res = await fetch(
            `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(trimmed)}&count=12&language=en&format=json`
          );
          if (res.ok) {
            const data = await res.json();
            results = data.results || [];
          }
        } catch {
          // Fallback to backend /api/places if direct fetch fails
          if (BASE) {
            const backRes = await fetch(`${BASE}/api/places?q=${encodeURIComponent(trimmed)}`);
            if (backRes.ok) {
              results = await backRes.json();
            }
          }
        }

        const formatted = (results || []).map((item, idx) => {
          const name = item.name || '';
          const state = item.admin1 || item.state || '';
          const country = item.country || '';
          const lat = item.latitude;
          const lon = item.longitude;
          const tz = item.timezone || 'UTC';
          const displayName = [name, state, country].filter(Boolean).join(', ');

          return {
            id: `${lat}_${lon}_${idx}`,
            name,
            state,
            country,
            latitude: lat,
            longitude: lon,
            timezone: tz,
            displayName
          };
        });

        setSuggestions(formatted);
        setShowDropdown(formatted.length > 0);
      } catch (err) {
        console.error('Error fetching place suggestions:', err);
        setSuggestions([]);
      } finally {
        setLoadingSuggestions(false);
      }
    }, 280);
  };

  const handleSelectPlace = (placeItem) => {
    setFormData((prev) => ({
      ...prev,
      place: placeItem.displayName,
      latitude: placeItem.latitude,
      longitude: placeItem.longitude,
      timezone: placeItem.timezone
    }));
    setHasSelectedFromList(true);
    setShowDropdown(false);
    setSuggestions([]);
  };

  const handleKeyDown = (e) => {
    if (!showDropdown || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === 'Enter') {
      if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
        e.preventDefault();
        handleSelectPlace(suggestions[selectedIndex]);
      }
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowDropdown(false);
    onSubmit(formData);
  };

  return (
    <div className="glass-panel" style={{ maxWidth: '520px', margin: '0 auto 2rem auto', position: 'relative' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', letterSpacing: '1px' }}>Cast Your Chart</h2>
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.3rem' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--color-gold-light)', fontSize: '0.9rem' }}>
            Date of Birth (YYYY-MM-DD)
          </label>
          <input 
            type="date"
            required
            value={formData.dob}
            onChange={(e) => setFormData({ ...formData, dob: e.target.value })}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--color-gold-light)', fontSize: '0.9rem' }}>
            Time of Birth (HH:MM 24hr)
          </label>
          <input 
            type="time"
            required
            value={formData.tob}
            onChange={(e) => setFormData({ ...formData, tob: e.target.value })}
          />
        </div>

        <div ref={wrapperRef} style={{ position: 'relative' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <label style={{ color: 'var(--color-gold-light)', fontSize: '0.9rem' }}>
              Place of Birth
            </label>
            {loadingSuggestions && (
              <span style={{ fontSize: '0.78rem', color: 'var(--color-gold-light)', opacity: 0.85, fontStyle: 'italic' }}>
                Searching cosmic atlas...
              </span>
            )}
          </div>

          <input 
            type="text"
            required
            autoComplete="off"
            placeholder="Type place (e.g. Kochi, Tokyo, London)..."
            value={formData.place}
            onChange={handlePlaceInputChange}
            onFocus={() => {
              if (suggestions.length > 0 && !hasSelectedFromList) {
                setShowDropdown(true);
              }
            }}
            onKeyDown={handleKeyDown}
          />

          {/* Autocomplete Dropdown */}
          {showDropdown && suggestions.length > 0 && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                marginTop: '6px',
                background: 'rgba(15, 12, 24, 0.97)',
                backdropFilter: 'blur(16px)',
                WebkitBackdropFilter: 'blur(16px)',
                border: '1px solid var(--color-gold-deep)',
                borderRadius: '8px',
                boxShadow: '0 12px 35px rgba(0, 0, 0, 0.8), 0 0 15px rgba(199, 161, 83, 0.2)',
                maxHeight: '260px',
                overflowY: 'auto',
                zIndex: 1000
              }}
            >
              <div style={{ padding: '0.4rem 0.8rem', borderBottom: '1px solid rgba(199, 161, 83, 0.15)', fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                Matching Worldwide Locations ({suggestions.length})
              </div>

              {suggestions.map((item, idx) => {
                const isHoveredOrActive = idx === selectedIndex;
                return (
                  <div
                    key={item.id}
                    onClick={() => handleSelectPlace(item)}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    style={{
                      padding: '0.65rem 0.9rem',
                      cursor: 'pointer',
                      borderBottom: idx < suggestions.length - 1 ? '1px solid rgba(255, 255, 255, 0.05)' : 'none',
                      background: isHoveredOrActive ? 'rgba(199, 161, 83, 0.18)' : 'transparent',
                      transition: 'background 0.15s ease',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '2px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ color: 'var(--color-gold-light)', fontSize: '0.9rem' }}>📍</span>
                      <span style={{ fontWeight: '600', color: isHoveredOrActive ? 'var(--color-gold-light)' : 'var(--color-text-main)', fontSize: '0.95rem' }}>
                        {item.name}
                      </span>
                      {(item.state || item.country) && (
                        <span style={{ color: 'var(--color-text-muted)', fontSize: '0.88rem' }}>
                          — {[item.state, item.country].filter(Boolean).join(', ')}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', paddingLeft: '1.3rem' }}>
                      Lat: {Number(item.latitude).toFixed(2)}°, Lon: {Number(item.longitude).toFixed(2)}°
                      {item.timezone ? ` • ${item.timezone}` : ''}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Confirmation badge when place is pinned */}
          {hasSelectedFromList && formData.latitude !== null && (
            <div style={{ 
              marginTop: '0.45rem', 
              fontSize: '0.78rem', 
              color: 'var(--color-gold-light)', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '6px',
              padding: '0.3rem 0.6rem',
              background: 'rgba(199, 161, 83, 0.08)',
              border: '1px solid rgba(199, 161, 83, 0.2)',
              borderRadius: '4px'
            }}>
              <span>✓ Coordinates pinned:</span>
              <span style={{ color: 'var(--color-text-main)' }}>
                {Number(formData.latitude).toFixed(2)}°N, {Number(formData.longitude).toFixed(2)}°E ({formData.timezone || 'UTC'})
              </span>
            </div>
          )}
        </div>

        <button 
          type="submit" 
          disabled={loading} 
          style={{ 
            marginTop: '0.8rem', 
            padding: '1rem', 
            fontWeight: '600',
            fontSize: '1.05rem',
            letterSpacing: '2px' 
          }}
        >
          {loading ? 'Calculating Koshas...' : 'Reveal Destiny'}
        </button>
      </form>
    </div>
  );
}
