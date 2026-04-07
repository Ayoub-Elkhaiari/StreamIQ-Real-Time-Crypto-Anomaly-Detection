import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts';
import styles from './Chart.module.css';

const AXIS_COLOR = '#94a3b8';
const GRID_COLOR = '#2a2a3a';

export default function VolumeChart({ data }) {
  const top10 = [...(data || [])].sort((a, b) => (b.total_volume || 0) - (a.total_volume || 0)).slice(0, 10);

  return (
    <div className={styles.card}>
      <h3>Volume by Top 10 Coins</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={top10}>
          <CartesianGrid stroke={GRID_COLOR} strokeDasharray="3 3" />
          <XAxis dataKey="symbol" tick={{ fill: AXIS_COLOR, fontSize: 12 }} axisLine={{ stroke: GRID_COLOR }} tickLine={{ stroke: GRID_COLOR }} />
          <YAxis tick={{ fill: AXIS_COLOR, fontSize: 12 }} axisLine={{ stroke: GRID_COLOR }} tickLine={{ stroke: GRID_COLOR }} />
          <Tooltip
            contentStyle={{ background: '#1e1e2e', border: '1px solid #6366f1', borderRadius: '8px', color: '#f1f5f9' }}
            labelStyle={{ color: '#f1f5f9' }}
          />
          <Bar dataKey="total_volume" radius={[6, 6, 0, 0]}>
            {top10.map((entry, i) => (
              <Cell key={i} fill={entry.is_anomaly ? '#ef4444' : '#6366f1'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
