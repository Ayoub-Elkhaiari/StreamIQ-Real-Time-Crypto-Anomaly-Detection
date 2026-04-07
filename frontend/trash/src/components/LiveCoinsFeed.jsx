import styles from './Table.module.css';

export default function LiveCoinsFeed({ coins }) {
  return <table className={styles.table}><thead><tr><th>Rank</th><th>Coin</th><th>Price</th><th>24h%</th><th>Volume</th><th>Score</th><th>Status</th></tr></thead><tbody>{(coins||[]).slice(0,50).map((c,i)=><tr key={`${c.coin_id}-${i}`} className={c.is_anomaly?styles.anomalyRow:''}><td>{c.market_cap_rank}</td><td>{c.symbol}</td><td>${Number(c.current_price||0).toFixed(4)}</td><td>{Number(c.price_change_percentage_24h||0).toFixed(2)}%</td><td>${Number(c.total_volume||0).toLocaleString()}</td><td>{Number(c.anomaly_score||0).toFixed(3)}</td><td><span className={c.severity==='HIGH'?styles.high:c.severity==='MEDIUM'?styles.medium:styles.normal}>{c.is_anomaly?'🚨 ANOM':'✅ OK'}</span></td></tr>)}</tbody></table>;
}
