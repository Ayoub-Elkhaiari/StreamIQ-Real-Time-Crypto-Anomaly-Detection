import styles from './Table.module.css';

export default function AnomalyTable({ anomalies }) {
  return <table className={styles.table}><thead><tr><th>Coin</th><th>Price</th><th>Score</th><th>24h%</th><th>Severity</th><th>Time</th></tr></thead><tbody>{(anomalies||[]).map((a,i)=><tr key={`${a.coin_id}-${i}`} className={styles.anomalyRow}><td>{a.symbol}</td><td>${Number(a.current_price||0).toFixed(4)}</td><td>{a.anomaly_score}</td><td>{Number(a.price_change_percentage_24h||0).toFixed(2)}%</td><td><span className={a.severity==='HIGH'?styles.high:a.severity==='MEDIUM'?styles.medium:styles.normal}>{a.severity}</span></td><td>{new Date(a.detected_at||a.processed_at||Date.now()).toLocaleTimeString()}</td></tr>)}</tbody></table>;
}
