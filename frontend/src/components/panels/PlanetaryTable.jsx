import React from 'react';

const thStyle = {
  textAlign: 'left',
  padding: '1rem',
  color: 'var(--color-gold-deep)',
  fontFamily: 'var(--font-ancient)',
  borderBottom: '1px solid var(--color-glass-border)',
  fontWeight: '600'
};

const tdStyle = {
  padding: '1rem',
  borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
  color: 'var(--color-text-main)'
};

const getDignity = (planetId, sign) => {
  // sign: 0=Aries, 1=Taurus, 2=Gemini, 3=Cancer, 4=Leo, 5=Virgo, 6=Libra, 7=Scorpio, 8=Sag, 9=Cap, 10=Aq, 11=Pisces
  const DIGNITIES = {
    'Su': { exalted: 0, own: [4], deb: 6, moola: 4 },
    'Mo': { exalted: 1, own: [3], deb: 7, moola: 1 },
    'Ma': { exalted: 9, own: [0, 7], deb: 3, moola: 0 },
    'Me': { exalted: 5, own: [2, 5], deb: 11, moola: 5 },
    'Ju': { exalted: 3, own: [8, 11], deb: 9, moola: 8 },
    'Ve': { exalted: 11, own: [1, 6], deb: 5, moola: 6 },
    'Sa': { exalted: 6, own: [9, 10], deb: 0, moola: 10 },
    'Ra': { exalted: 1, own: [10], deb: 7, moola: 2 }, // Using Taurus/Scorpio for nodes as one common system
    'Ke': { exalted: 7, own: [7], deb: 1, moola: 8 }
  };
  
  const rules = DIGNITIES[planetId];
  if (!rules) return 'Neutral';
  
  if (rules.exalted === sign) return <span style={{ color: '#88ff88', fontWeight: 'bold' }}>Exalted</span>;
  if (rules.deb === sign) return <span style={{ color: '#ff8888', fontWeight: 'bold' }}>Debilitated</span>;
  if (rules.moola === sign) return <span style={{ color: '#88aaff', fontWeight: 'bold' }}>Moolatrikona</span>;
  if (rules.own.includes(sign)) return <span style={{ color: '#aaddff' }}>Own Sign</span>;
  
  return <span style={{ color: 'var(--color-text-muted)' }}>Neutral</span>;
};


export default function PlanetaryTable({ planets }) {
  // Sort planets using a stable order if desired, or just display as provided
  return (
    <div className="glass-panel" style={{ overflowX: 'auto' }}>
      <h3 style={{ marginBottom: '1rem', textAlign: 'center' }}>Planetary Dispositions</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.95rem' }}>
        <thead>
          <tr>
            <th style={thStyle}>Graha</th>
            <th style={thStyle}>Sign</th>
            <th style={thStyle}>Degree</th>
            <th style={thStyle}>Nakshatra</th>
            <th style={thStyle}>House</th>
            <th style={thStyle}>Dignity</th>
            <th style={thStyle}>Movement</th>
          </tr>
        </thead>
        <tbody>
          {planets.map((p) => (
            <tr key={p.id} style={{ transition: 'background 0.2s' }} onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'} onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
              <td style={{ ...tdStyle, fontWeight: '600', color: 'var(--color-gold-light)' }}>
                {p.name} ({p.id})
              </td>
              <td style={tdStyle}>{p.sign_name}</td>
              <td style={tdStyle}>{p.degree.toFixed(2)}°</td>
              <td style={tdStyle}>{p.nakshatra} p.{p.pada}</td>
              <td style={tdStyle}>{p.house}</td>
              <td style={tdStyle}>{getDignity(p.id, p.sign)}</td>
              <td style={tdStyle}>
                {p.retrograde ? <span style={{ color: '#ff8888' }} title="Retrograde">Retrograde (℞)</span> : <span style={{ color: '#88ff88' }}>Direct</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
