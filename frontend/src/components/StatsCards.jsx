import styles from './StatsCards.module.css';

export default function StatsCards({ stats }) {
  return (
    <div className={styles.grid}>
      <div className={styles.card}>
        <div className={styles.label}>Snapshots Processed</div>
        <strong className={styles.value}>{stats.total_snapshots || 0}</strong>
      </div>
      <div className={`${styles.card} ${styles.accent}`}>
        <div className={styles.label}>Anomalies Detected</div>
        <strong className={styles.value}>{stats.total_anomalies || 0}</strong>
      </div>
      <div className={styles.card}>
        <div className={styles.label}>Anomaly %</div>
        <strong className={styles.value}>{stats.anomaly_rate_pct || 0}%</strong>
      </div>
      <div className={styles.card}>
        <div className={styles.label}>Coins Tracked</div>
        <strong className={styles.value}>{stats.coins_tracked || 0}</strong>
      </div>
    </div>
  );
}
