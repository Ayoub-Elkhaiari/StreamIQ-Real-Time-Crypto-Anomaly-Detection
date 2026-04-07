import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts';
import styles from './Chart.module.css';

export default function VolumeChart({ data }) {
  const top10 = [...(data || [])].sort((a, b) => (b.total_volume || 0) - (a.total_volume || 0)).slice(0, 10);
  return <div className={styles.card}><h3>Volume by Top 10 Coins</h3><ResponsiveContainer width="100%" height={260}><BarChart data={top10}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="symbol"/><YAxis/><Tooltip/><Bar dataKey="total_volume">{top10.map((entry, i) => <Cell key={i} fill={entry.is_anomaly ? '#EF4444' : '#2563EB'} />)}</Bar></BarChart></ResponsiveContainer></div>;
}
