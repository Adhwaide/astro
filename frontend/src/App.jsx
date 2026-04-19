import React, { useState } from 'react';
import BirthForm from './components/BirthForm';
import SouthIndianChart from './components/charts/SouthIndianChart';
import NorthIndianChart from './components/charts/NorthIndianChart';
import PlanetaryTable from './components/panels/PlanetaryTable';
import DashaTree from './components/panels/DashaTree';
import ReportPanel from './components/panels/ReportPanel';
import LifeReportPanel from './components/panels/LifeReportPanel';
import { useChartData } from './hooks/useChartData';
import './index.css';

function App() {
  const {
    loading, error,
    chartData, dashaData, divisionalData, divisionalLoading, reportData,
    calculateDashasAndChart, fetchDivisional
  } = useChartData();

  const [activeTab, setActiveTab] = useState('chart');
  const [chartStyle, setChartStyle] = useState('south');
  const [selectedDivisional, setSelectedDivisional] = useState('D9');
  const [formDataCache, setFormDataCache] = useState(null);

  const handleSubmit = async (formData) => {
    setFormDataCache(formData);
    await calculateDashasAndChart(formData);
  };

  const handleDivisionalChange = async (chartType) => {
    setSelectedDivisional(chartType);
    if (formDataCache) {
      await fetchDivisional(formDataCache, chartType);
    }
  };

  // Decide which data to render when the divisional tab is active
  const divChartData = divisionalData || null;

  const renderChart = (data) => {
    if (!data) return null;
    if (chartStyle === 'south') {
      return <SouthIndianChart chartData={data} />;
    }
    return <NorthIndianChart chartData={data} />;
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
      <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '0.5rem', textShadow: '0 0 15px var(--color-gold-glow)' }}>
          Jyotisha Engine
        </h1>
        <p style={{ color: 'var(--color-text-muted)', letterSpacing: '2px' }}>MODERN VEDIC ASTROLOGY</p>
      </header>

      <BirthForm onSubmit={handleSubmit} loading={loading} />

      {error && (
        <div className="glass-panel" style={{ borderColor: '#ff4444', color: '#ffaaaa', marginBottom: '2rem', textAlign: 'center' }}>
          <strong>Oracle Interrupted:</strong> {error}
        </div>
      )}

      {chartData && dashaData && (
        <div style={{ animation: 'fadeIn 1s ease' }}>
          <div className="glass-panel" style={{ marginBottom: '2rem', textAlign: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '1.5rem' }}>
              Lagna: <span style={{ color: 'var(--color-text-main)' }}>{chartData.lagna.sign_name}</span> at {chartData.lagna.degree.toFixed(2)}°
            </h3>
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
              Ayanamsha: {chartData.meta.ayanamsha} ({chartData.meta.ayanamsha_value.toFixed(4)}°)
            </p>
          </div>
          
          {/* Tab Buttons */}
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', marginBottom: '2rem', flexWrap: 'wrap' }}>
            {['chart', 'divisional', 'dashas', 'report', 'life-report'].map(tab => (
              <button
                key={tab}
                onClick={() => {
                  setActiveTab(tab);
                  // Auto-fetch divisional data when tab is first selected
                  if (tab === 'divisional' && !divisionalData && formDataCache) {
                    fetchDivisional(formDataCache, selectedDivisional);
                  }
                }}
                style={{
                  background: activeTab === tab ? 'var(--color-gold-glow)' : 'transparent',
                  fontSize: '0.85rem',
                  padding: '0.6rem 1.2rem',
                }}
              >
                {tab === 'chart' && 'Rasi Chart (D1)'}
                {tab === 'divisional' && 'Divisional Charts'}
                {tab === 'dashas' && 'Vimshottari Dashas'}
                {tab === 'report' && 'Analysis Report'}
                {tab === 'life-report' && 'Life Report'}
              </button>
            ))}
          </div>

          {/* Chart Style Toggle (shared by Rasi & Divisional tabs) */}
          {(activeTab === 'chart' || activeTab === 'divisional') && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <button 
                onClick={() => setChartStyle('south')}
                style={{ 
                  padding: '0.5rem 1rem', fontSize: '0.8rem',
                  background: chartStyle === 'south' ? 'rgba(199, 161, 83, 0.2)' : 'transparent',
                  border: '1px solid var(--color-gold-deep)'
                }}
              >
                South Indian
              </button>
              <button 
                onClick={() => setChartStyle('north')}
                style={{ 
                  padding: '0.5rem 1rem', fontSize: '0.8rem',
                  background: chartStyle === 'north' ? 'rgba(199, 161, 83, 0.2)' : 'transparent',
                  border: '1px solid var(--color-gold-deep)'
                }}
              >
                North Indian
              </button>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr)', gap: '2rem' }}>
            {/* D1 Rasi Chart Tab */}
            {activeTab === 'chart' && (
              <>
                {renderChart(chartData)}
                <PlanetaryTable planets={chartData.planets} />
              </>
            )}

            {/* Divisional Charts Tab */}
            {activeTab === 'divisional' && (
              <>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                  {['D2', 'D9', 'D10', 'D30'].map(dt => (
                    <button
                      key={dt}
                      onClick={() => handleDivisionalChange(dt)}
                      style={{
                        padding: '0.5rem 1rem', fontSize: '0.8rem',
                        background: selectedDivisional === dt ? 'rgba(199, 161, 83, 0.2)' : 'transparent',
                        border: '1px solid var(--color-gold-deep)',
                      }}
                    >
                      {dt === 'D2' && 'D2 (Hora)'}
                      {dt === 'D9' && 'D9 (Navamsha)'}
                      {dt === 'D10' && 'D10 (Dasamsa)'}
                      {dt === 'D30' && 'D30 (Trimsamsa)'}
                    </button>
                  ))}
                </div>

                {divisionalLoading && (
                  <div className="glass-panel" style={{ textAlign: 'center', color: 'var(--color-gold-light)' }}>
                    Calculating {selectedDivisional} chart...
                  </div>
                )}

                {divChartData && !divisionalLoading && (
                  <>
                    <div className="glass-panel" style={{ textAlign: 'center', padding: '1rem' }}>
                      <h4 style={{ margin: 0 }}>
                        {selectedDivisional} Lagna: <span style={{ color: 'var(--color-text-main)' }}>{divChartData.lagna.sign_name}</span>
                      </h4>
                    </div>
                    {renderChart(divChartData)}
                    <PlanetaryTable planets={divChartData.planets} />
                  </>
                )}
              </>
            )}
            
            {/* Dashas Tab */}
            {activeTab === 'dashas' && (
              <DashaTree dashaData={dashaData} />
            )}
            
            {/* Existing Analysis Report Tab */}
            {activeTab === 'report' && (
              <ReportPanel chartData={chartData} />
            )}

            {/* New Structured Life Report Tab */}
            {activeTab === 'life-report' && reportData && (
              <LifeReportPanel reportData={reportData} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
