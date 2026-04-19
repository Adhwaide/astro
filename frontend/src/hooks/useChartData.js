import { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const useChartData = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [dashaData, setDashaData] = useState(null);
  const [divisionalData, setDivisionalData] = useState(null);
  const [divisionalLoading, setDivisionalLoading] = useState(false);
  const [reportData, setReportData] = useState(null);

  const calculateDashasAndChart = async (formData) => {
    setLoading(true);
    setError(null);
    setDivisionalData(null);
    setReportData(null);
    try {
      // Execute all three backend calls in parallel
      const [chartRes, dashaRes, reportRes] = await Promise.all([
        fetch(`${API_BASE_URL}/chart`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        }),
        fetch(`${API_BASE_URL}/dasha`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        }),
        fetch(`${API_BASE_URL}/report`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        })
      ]);

      if (!chartRes.ok) {
        const err = await chartRes.json();
        throw new Error(err.detail || 'Chart calculation failed');
      }
      if (!dashaRes.ok) {
        const err = await dashaRes.json();
        throw new Error(err.detail || 'Dasha calculation failed');
      }

      const chart = await chartRes.json();
      const dashas = await dashaRes.json();
      const report = reportRes.ok ? await reportRes.json() : null;

      setChartData(chart);
      setDashaData(dashas);
      setReportData(report);
      return true;
    } catch (err) {
        console.error('API Error:', err);
        setError(err.message || 'Error communicating with backend');
        return false;
    } finally {
        setLoading(false);
    }
  };

  const fetchDivisional = async (formData, chartType) => {
    setDivisionalLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/divisional`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, chart_type: chartType }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Divisional chart failed');
      }

      const data = await res.json();
      setDivisionalData(data);
      return true;
    } catch (err) {
      console.error('API Error:', err);
      setError(err.message || 'Error fetching divisional chart');
      return false;
    } finally {
      setDivisionalLoading(false);
    }
  };

  return {
    loading, error,
    chartData, dashaData, divisionalData, divisionalLoading, reportData,
    calculateDashasAndChart, fetchDivisional
  };
};
