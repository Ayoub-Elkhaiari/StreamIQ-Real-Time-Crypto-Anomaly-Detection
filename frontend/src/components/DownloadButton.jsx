import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import styles from './DownloadButton.module.css';

export default function DownloadButton({ stats, anomalies }) {
  const onExport = () => {
    const doc = new jsPDF({ orientation: 'landscape' });
    const now = new Date();
    const stamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}-${String(now.getHours()).padStart(2, '0')}-${String(now.getMinutes()).padStart(2, '0')}`;
    doc.text('StreamIQ — Crypto Anomaly Detection Report', 14, 16);
    doc.text(`Generated: ${now.toISOString()}`, 14, 24);
    doc.text(`Snapshots: ${stats.total_snapshots || 0}`, 14, 32);
    doc.text(`Anomalies: ${stats.total_anomalies || 0}`, 14, 38);
    doc.text(`Anomaly Rate: ${stats.anomaly_rate_pct || 0}%`, 14, 44);
    doc.text(`Coins Tracked: ${stats.coins_tracked || 0}`, 14, 50);

    autoTable(doc, {
      startY: 56,
      head: [['Coin', 'Price', 'Score', '24h%', 'Severity', 'Time']],
      body: (anomalies || []).map((a) => [a.symbol, a.current_price, a.anomaly_score, a.price_change_percentage_24h, a.severity, a.detected_at || a.processed_at]),
    });
    doc.save(`streamiq-crypto-report-${stamp}.pdf`);
  };

  return (
    <button type="button" className={styles.button} onClick={onExport}>
      📥 Export PDF
    </button>
  );
}
