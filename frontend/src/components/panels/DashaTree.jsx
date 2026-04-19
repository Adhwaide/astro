import React, { useState } from 'react';
import { formatDate } from '../../utils/formatters';

const LEVEL_LABELS = ['Mahadasha', 'Antardasha', 'Pratyantardasha', 'Sookshmadasha', 'Pranadasha'];

const PeriodRow = ({ period, level, isOpen, onToggle, isCurrent, maxLevel = 4 }) => {
  const paddingLeft = `${level * 1.5 + 0.5}rem`;
  const isExpandable = level < maxLevel;

  return (
    <div style={{
      padding: '0.7rem 0.8rem',
      paddingLeft,
      borderBottom: '1px solid rgba(255,255,255,0.04)',
      cursor: isExpandable ? 'pointer' : 'default',
      background: isCurrent ? 'rgba(199, 161, 83, 0.1)' : 'transparent',
      transition: 'var(--transition-smooth)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      fontSize: level >= 3 ? '0.85rem' : '1rem',
    }}
    onClick={isExpandable ? onToggle : undefined}
    onMouseEnter={e => !isCurrent && (e.currentTarget.style.background = 'rgba(255,255,255,0.03)')}
    onMouseLeave={e => !isCurrent && (e.currentTarget.style.background = 'transparent')}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        {isExpandable && (
          <span style={{
            fontSize: '0.7rem', color: 'var(--color-gold-deep)',
            transition: 'transform 0.2s',
            transform: isOpen ? 'rotate(90deg)' : 'rotate(0)',
            display: 'inline-block',
          }}>
            ▶
          </span>
        )}
        {!isExpandable && <span style={{ width: '0.7rem' }} />}
        <span style={{ 
          fontFamily: level <= 1 ? 'var(--font-ancient)' : 'var(--font-modern)', 
          color: isCurrent ? 'var(--color-gold-light)' : 'var(--color-text-main)',
          fontSize: level === 0 ? '1.05rem' : level === 1 ? '0.95rem' : '0.85rem',
          fontWeight: level <= 1 ? '600' : '400',
        }}>
          {period.lord_name}
        </span>
        {isCurrent && (
          <span style={{
            fontSize: '0.6rem', background: 'var(--color-gold-deep)',
            color: '#000', padding: '2px 5px', borderRadius: '3px', fontWeight: '700'
          }}>
            ACTIVE
          </span>
        )}
        <span style={{ color: 'var(--color-text-muted)', fontSize: '0.7rem', opacity: 0.6 }}>
          {LEVEL_LABELS[level]}
        </span>
      </div>
      <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
        {formatDate(period.start_date)} — {formatDate(period.end_date)}
      </div>
    </div>
  );
};

export default function DashaTree({ dashaData }) {
  const [openNodes, setOpenNodes] = useState({});

  const toggleNode = (key) => {
    setOpenNodes(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const { current_period } = dashaData;

  const isCurrentAt = (level, lords) => {
    const levelKeys = ['mahadasha', 'antardasha', 'pratyantardasha', 'sookshmadasha', 'pranadasha'];
    for (let i = 0; i <= level; i++) {
      const cp = current_period?.[levelKeys[i]];
      if (!cp || cp.lord !== lords[i]) return false;
    }
    return true;
  };

  const getChildren = (period, level) => {
    if (level === 0) return period.antardasha || [];
    if (level === 1) return period.pratyantardasha || [];
    if (level === 2) return period.sookshmadasha || [];
    if (level === 3) return period.pranadasha || [];
    return [];
  };

  const renderLevel = (periods, level, parentKey, parentLords) => {
    return periods.map((period, i) => {
      const key = `${parentKey}-${level}-${i}`;
      const lords = [...parentLords, period.lord];
      const isCurrent = isCurrentAt(level, lords);
      const children = getChildren(period, level);
      const isOpen = openNodes[key];

      return (
        <React.Fragment key={key}>
          <PeriodRow
            period={period}
            level={level}
            isOpen={isOpen}
            onToggle={() => toggleNode(key)}
            isCurrent={isCurrent}
            maxLevel={4}
          />
          {isOpen && children.length > 0 && renderLevel(children, level + 1, key, lords)}
        </React.Fragment>
      );
    });
  };

  return (
    <div className="glass-panel">
      <h3 style={{ textAlign: 'center', marginBottom: '0.5rem' }}>Vimshottari Dasha</h3>
      <p style={{ textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
        Moon Nakshatra: {dashaData.moon_nakshatra} | Starting Lord: {dashaData.starting_lord_name}
      </p>
      <p style={{ textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '0.75rem', marginBottom: '2rem', opacity: 0.7 }}>
        5 levels: Maha → Antar → Pratyantar → Sookshma → Prana
      </p>

      <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        {renderLevel(dashaData.mahadasha, 0, 'root', [])}
      </div>
    </div>
  );
}
