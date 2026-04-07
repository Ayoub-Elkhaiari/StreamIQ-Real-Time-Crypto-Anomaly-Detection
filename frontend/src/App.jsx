import { useEffect, useMemo, useState } from 'react';
import AnomalyChart from './components/AnomalyChart';
import AnomalyTable from './components/AnomalyTable';
import DownloadButton from './components/DownloadButton';
import LiveCoinsFeed from './components/LiveCoinsFeed';
import StatsCards from './components/StatsCards';
import VolumeChart from './components/VolumeChart';
import styles from './components/App.module.css';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function fetchJson(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`${path} failed with status ${response.status}`);
  }
  return response.json();
}

export default function App() {
  const [stats, setStats] = useState({ total_snapshots: 0, total_anomalies: 0, anomaly_rate_pct: 0, coins_tracked: 50, last_updated: null });
  const [coins, setCoins] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [anomalySeries, setAnomalySeries] = useState([]);
  const [topAnomalies, setTopAnomalies] = useState([]);
  const [lastDataAt, setLastDataAt] = useState(null);

  useEffect(() => {
    const pollFast = async () => {
      try {
        const [s, c, a] = await Promise.all([
          fetchJson('/stats'),
          fetchJson('/recent-coins?limit=50'),
          fetchJson('/recent-anomalies?limit=20'),
        ]);
        setStats(s);
        setCoins(Array.isArray(c) ? c : []);
        setAnomalies(Array.isArray(a) ? a : []);
        setLastDataAt(Date.now());
      } catch (error) {
        console.error('Fast polling failed:', error);
      }
    };
    pollFast();
    const id = setInterval(pollFast, 30000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const pollSlow = async () => {
      try {
        const [series, top] = await Promise.all([
          fetchJson('/anomalies-over-time?hours=6'),
          fetchJson('/top-anomalies'),
        ]);
        setAnomalySeries(Array.isArray(series) ? series : []);
        setTopAnomalies(Array.isArray(top) ? top : []);
        setLastDataAt(Date.now());
      } catch (error) {
        console.error('Slow polling failed:', error);
      }
    };
    pollSlow();
    const id = setInterval(pollSlow, 60000);
    return () => clearInterval(id);
  }, []);

  const isLive = useMemo(() => lastDataAt && Date.now() - lastDataAt <= 60000, [lastDataAt]);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}><span className={styles.logoText}>⚡ StreamIQ</span><span className={styles.subtitle}>Crypto Anomaly Detection</span></h1>
        <div className={styles.liveWrap}><span className={isLive ? styles.dotLive : styles.dotIdle}>●</span>{isLive ? 'LIVE' : 'IDLE'}</div>
      </header>

      <StatsCards stats={stats} />

      <div className={styles.grid2}>
        <AnomalyChart data={anomalySeries} />
        <VolumeChart data={coins} />
      </div>

      <section className={styles.panel}>
        <div className={styles.panelHeader}><h2>🚨 Recent Anomalies</h2><DownloadButton stats={stats} anomalies={anomalies} /></div>
        <AnomalyTable anomalies={anomalies} />
      </section>

      <section className={styles.panel}>
        <h2>📊 Live Coins Feed (50 coins, updates every 30s)</h2>
        <LiveCoinsFeed coins={coins} topAnomalies={topAnomalies} />
      </section>
    </div>
  );
}
