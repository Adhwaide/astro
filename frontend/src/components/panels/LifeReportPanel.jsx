import React from 'react';

const SECTION_CONFIG = {
  health: { title: 'Health & Vitality', icon: '🏥' },
  career: { title: 'Career & Profession', icon: '💼' },
  relationships: { title: 'Relationships & Marriage', icon: '💑' },
  spirituality: { title: 'Spirituality & Dharma', icon: '🕉️' },
  current_period_summary: { title: 'Current Dasha Period', icon: '⏳' },
};

const SectionCard = ({ sectionKey, data }) => {
  const config = SECTION_CONFIG[sectionKey] || { title: sectionKey, icon: '📄' };

  return (
    <div className="glass-panel" style={{ marginBottom: '1.5rem' }}>
      <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <span style={{ fontSize: '1.3rem' }}>{config.icon}</span>
        {config.title}
      </h3>

      <p style={{
        color: 'var(--color-text-main)',
        lineHeight: '1.7',
        fontSize: '0.95rem',
        marginBottom: '1.2rem',
        padding: '1rem',
        background: 'rgba(199, 161, 83, 0.05)',
        borderLeft: '3px solid var(--color-gold-deep)',
        borderRadius: '0 6px 6px 0',
      }}>
        {data.summary}
      </p>

      {data.key_factors && data.key_factors.length > 0 && (
        <div>
          <h4 style={{
            color: 'var(--color-gold-deep)',
            fontSize: '0.85rem',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            marginBottom: '0.8rem',
          }}>
            Key Factors
          </h4>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {data.key_factors.map((factor, i) => (
              <li key={i} style={{
                padding: '0.6rem 0.8rem',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
                color: 'var(--color-text-main)',
                fontSize: '0.9rem',
                lineHeight: '1.5',
                display: 'flex',
                gap: '0.5rem',
              }}>
                <span style={{ color: 'var(--color-gold-light)', flexShrink: 0 }}>•</span>
                {factor}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default function LifeReportPanel({ reportData }) {
  if (!reportData) return null;

  const sections = ['health', 'career', 'relationships', 'spirituality', 'current_period_summary'];

  return (
    <div>
      <div className="glass-panel" style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h2 style={{ margin: 0 }}>Vedic Life Report</h2>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
          Based on classical Parashari analysis of house lords, dignities, and planetary dispositions
        </p>
      </div>

      {sections.map(key => (
        reportData[key] && <SectionCard key={key} sectionKey={key} data={reportData[key]} />
      ))}

      <div style={{
        textAlign: 'center',
        color: 'var(--color-text-muted)',
        fontSize: '0.8rem',
        fontStyle: 'italic',
        marginTop: '1rem',
      }}>
        This report is generated using classical Vedic rules and should be contextualized by a human astrologer.
      </div>
    </div>
  );
}
