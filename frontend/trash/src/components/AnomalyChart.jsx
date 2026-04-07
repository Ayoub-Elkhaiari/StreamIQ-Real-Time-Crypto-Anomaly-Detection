import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import styles from './Chart.module.css';

export default function AnomalyChart({ data }) {
  return <div className={styles.card}><h3>Anomalies Over Time (6h)</h3><ResponsiveContainer width="100%" height={260}><LineChart data={data}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="time_bucket"/><YAxis/><Tooltip/><Line type="monotone" dataKey="anomaly_count" stroke="#2563EB"/></LineChart></ResponsiveContainer></div>;
}
