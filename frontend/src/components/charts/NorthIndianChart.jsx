import React from 'react';

const NORTH_HOUSES = [
  // house index 0 to 11 (H1 to H12)
  // Polygon points, text anchor center
  { id: 0, points: "200,0 300,100 200,200 100,100", center: [200, 85], signPos: [200, 15] },
  { id: 1, points: "0,0 100,100 200,0", center: [100, 45], signPos: [40, 20] },
  { id: 2, points: "0,0 0,200 100,100", center: [45, 100], signPos: [15, 50] },
  { id: 3, points: "0,200 100,100 200,200 100,300", center: [85, 200], signPos: [20, 200] },
  { id: 4, points: "0,400 0,200 100,300", center: [45, 300], signPos: [15, 350] },
  { id: 5, points: "0,400 100,300 200,400", center: [100, 355], signPos: [40, 380] },
  { id: 6, points: "200,400 100,300 200,200 300,300", center: [200, 315], signPos: [200, 380] },
  { id: 7, points: "400,400 200,400 300,300", center: [300, 355], signPos: [360, 380] },
  { id: 8, points: "400,400 300,300 400,200", center: [355, 300], signPos: [385, 350] },
  { id: 9, points: "400,200 300,300 200,200 300,100", center: [315, 200], signPos: [380, 200] },
  { id: 10, points: "400,0 400,200 300,100", center: [355, 100], signPos: [385, 50] },
  { id: 11, points: "400,0 300,100 200,0", center: [300, 45], signPos: [360, 20] }
];

export default function NorthIndianChart({ chartData }) {
  if (!chartData) return null;

  const { planets, lagna } = chartData;
  const lagnaSign = lagna.sign;

  return (
    <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto', display: 'flex', justifyContent: 'center' }}>
      <svg 
        viewBox="0 0 400 400" 
        style={{ width: '100%', maxWidth: '400px', height: 'auto', background: 'rgba(0,0,0,0.2)', border: '2px solid var(--color-gold-deep)', borderRadius: '4px' }}
      >
        <defs>
          <style>{`
            .house-bg { fill: transparent; stroke: var(--color-gold-deep); stroke-width: 2px; transition: fill 0.3s ease; }
            .house-bg:hover { fill: rgba(255, 255, 255, 0.05); }
            .lagna-bg { fill: rgba(199, 161, 83, 0.15); }
            .planet-text { font-size: 14px; fill: var(--color-text-main); font-weight: bold; text-anchor: middle; dominant-baseline: middle; }
            .sign-text { font-size: 12px; fill: var(--color-text-muted); opacity: 0.7; font-weight: bold; text-anchor: middle; dominant-baseline: middle; }
            .degree-text { font-size: 10px; fill: var(--color-text-muted); text-anchor: middle; dominant-baseline: middle; opacity: 0.8; }
          `}</style>
        </defs>

        {/* Draw outer border and lines */}
        <rect x="0" y="0" width="400" height="400" fill="none" stroke="var(--color-gold-deep)" strokeWidth="4" />
        <line x1="0" y1="0" x2="400" y2="400" stroke="var(--color-gold-deep)" strokeWidth="2" />
        <line x1="0" y1="400" x2="400" y2="0" stroke="var(--color-gold-deep)" strokeWidth="2" />
        <polygon points="200,0 400,200 200,400 0,200" fill="none" stroke="var(--color-gold-deep)" strokeWidth="2" />

        {/* Draw contents for each house */}
        {NORTH_HOUSES.map((house) => {
          const signIdx = (lagnaSign + house.id) % 12;
          const signNumber = signIdx + 1; // 1 to 12
          const housePlanets = planets.filter(p => p.sign === signIdx);
          
          const isLagna = house.id === 0;

          // Compute planet placement offsets simply
          // If many planets, stack them
          return (
            <g key={house.id}>
              {/* Invisible interactive polygon overlay */}
              <polygon 
                points={house.points} 
                className={`house-bg ${isLagna ? 'lagna-bg' : ''}`}
                onMouseEnter={(e) => { e.target.style.fill = 'rgba(255,255,255,0.05)' }}
                onMouseLeave={(e) => { e.target.style.fill = isLagna ? 'rgba(199, 161, 83, 0.15)' : 'transparent' }}
              />
              
              {/* Zodiac sign number */}
              <text x={house.signPos[0]} y={house.signPos[1]} className="sign-text">
                {signNumber}
              </text>
              
              {isLagna && (
                <text x={house.center[0]} y={house.center[1] - 20} className="sign-text" style={{ fill: 'var(--color-gold-light)', opacity: 1, fontSize: '10px' }}>
                  ASC
                </text>
              )}

              {/* Planets */}
              {housePlanets.map((p, i) => {
                const yOffset = (i - (housePlanets.length - 1) / 2) * 16;
                return (
                  <text key={p.id} x={house.center[0]} y={house.center[1] + yOffset} className="planet-text">
                    {p.id} <tspan className="degree-text" dx="2">{p.degree.toFixed(0)}°{p.retrograde ? '℞' : ''}</tspan>
                  </text>
                );
              })}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
