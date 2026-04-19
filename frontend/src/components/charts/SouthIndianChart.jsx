import React from 'react';

// South Indian Layout fixes signs to absolute positions:
// Pisces (11) at top-left.
//  11 | 0  | 1  | 2  
//  10 |         | 3
//  9  |         | 4
//  8  | 7  | 6  | 5

const SOUTH_BOXES = [
  { id: 11, name: 'Pisces', x: 0, y: 0 },
  { id: 0, name: 'Aries', x: 100, y: 0 },
  { id: 1, name: 'Taurus', x: 200, y: 0 },
  { id: 2, name: 'Gemini', x: 300, y: 0 },
  { id: 10, name: 'Aquarius', x: 0, y: 100 },
  { id: 3, name: 'Cancer', x: 300, y: 100 },
  { id: 9, name: 'Capricorn', x: 0, y: 200 },
  { id: 4, name: 'Leo', x: 300, y: 200 },
  { id: 8, name: 'Sagittarius', x: 0, y: 300 },
  { id: 7, name: 'Scorpio', x: 100, y: 300 },
  { id: 6, name: 'Libra', x: 200, y: 300 },
  { id: 5, name: 'Virgo', x: 300, y: 300 }
];

export default function SouthIndianChart({ chartData }) {
  if (!chartData) return null;

  const { planets, lagna } = chartData;

  return (
    <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto', display: 'flex', justifyContent: 'center' }}>
      <svg 
        viewBox="0 0 400 400" 
        style={{ width: '100%', maxWidth: '400px', height: 'auto', background: 'var(--color-gold-deep)', border: '4px solid var(--color-gold-deep)', borderRadius: '4px' }}
      >
        <defs>
          <style>{`
            .south-bg { fill: rgba(0,0,0,0.2); stroke: var(--color-glass-border); stroke-width: 1px; transition: fill 0.3s ease; }
            .south-bg:hover { fill: rgba(255, 255, 255, 0.05); }
            .south-lagna-bg { fill: rgba(199, 161, 83, 0.15); }
            .south-planet-text { font-size: 13px; fill: var(--color-text-main); font-weight: bold; }
            .south-sign-text { font-size: 10px; fill: var(--color-text-muted); text-transform: uppercase; }
            .south-degree-text { font-size: 10px; fill: var(--color-text-muted); opacity: 0.8; }
          `}</style>
        </defs>

        {/* Central decoration area */}
        <rect x="100" y="100" width="200" height="200" fill="transparent" />
        <text x="200" y="190" textAnchor="middle" style={{ fontSize: '32px', fill: 'var(--color-gold-deep)', fontFamily: 'var(--font-ancient)', opacity: 0.8 }}>Rasi</text>
        <text x="200" y="215" textAnchor="middle" style={{ fontSize: '12px', fill: 'var(--color-gold-deep)', letterSpacing: '2px', opacity: 0.8 }}>SOUTH INDIAN</text>

        {SOUTH_BOXES.map((box) => {
          const isLagna = lagna.sign === box.id;
          const boxPlanets = planets.filter(p => p.sign === box.id);
          
          return (
            <g key={box.id} transform={`translate(${box.x}, ${box.y})`}>
              {/* Box background */}
              <rect 
                width="98" 
                height="98" 
                x="1" 
                y="1" 
                className={`south-bg ${isLagna ? 'south-lagna-bg' : ''}`}
                onMouseEnter={(e) => { e.target.style.fill = 'rgba(255,255,255,0.05)' }}
                onMouseLeave={(e) => { e.target.style.fill = isLagna ? 'rgba(199, 161, 83, 0.15)' : 'rgba(0,0,0,0.2)' }}
              />
              
              {/* Sign Name */}
              <text x="8" y="20" className="south-sign-text">{box.name}</text>

              {/* ASC marker */}
              {isLagna && (
                <text x="75" y="20" className="south-sign-text" style={{ fill: 'var(--color-gold-light)', fontWeight: 'bold' }}>
                  ASC
                </text>
              )}

              {/* Planets */}
              {boxPlanets.map((p, i) => (
                <g key={p.id} transform={`translate(8, ${35 + i * 16})`}>
                  <text className="south-planet-text">{p.id}</text>
                  <text x="65" className="south-degree-text" textAnchor="end">
                    {p.degree.toFixed(0)}°{p.retrograde ? '℞' : ''}
                  </text>
                </g>
              ))}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
