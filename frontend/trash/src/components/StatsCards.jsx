import styles from './StatsCards.module.css';

export default function StatsCards({ stats }) {
  return (
    <div className={styles.grid}>
      <div className={styles.card}><div>Snapshots Processed</div><strong>{stats.total_snapshots || 0}</strong></div>
      <div className={`${styles.card} ${styles.blue}`}><div>Anomalies Detected</div><strong>{stats.total_anomalies || 0}</strong></div>
      <div className={styles.card}><div>Anomaly %</div><strong>{stats.anomaly_rate_pct || 0}%</strong></div>
      <div className={styles.card}><div>Coins Tracked</div><strong>{stats.coins_tracked || 0}</strong></div>
    </div>
  );
}
