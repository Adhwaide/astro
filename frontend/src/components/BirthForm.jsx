import { useState } from 'react';

export default function BirthForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    dob: '2004-02-28',
    tob: '01:15',
    place: 'Kochi, Kerala, India'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="glass-panel" style={{ maxWidth: '500px', margin: '0 auto 2rem auto' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Cast Your Chart</h2>
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--color-gold-light)', fontSize: '0.9rem' }}>
            Date of Birth (YYYY-MM-DD)
          </label>
          <input 
            type="date"
            required
            value={formData.dob}
            onChange={(e) => setFormData({...formData, dob: e.target.value})}
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
            onChange={(e) => setFormData({...formData, tob: e.target.value})}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--color-gold-light)', fontSize: '0.9rem' }}>
            Place of Birth
          </label>
          <input 
            type="text"
            required
            placeholder="e.g. Kochi, Kerala, India"
            value={formData.place}
            onChange={(e) => setFormData({...formData, place: e.target.value})}
          />
        </div>

        <button type="submit" disabled={loading} style={{ marginTop: '1rem', padding: '1rem' }}>
          {loading ? 'Calculating Koshas...' : 'Reveal Destiny'}
        </button>
      </form>
    </div>
  );
}
