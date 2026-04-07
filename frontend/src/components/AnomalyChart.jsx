import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import styles from './Chart.module.css';

const AXIS_COLOR = '#94a3b8';
const GRID_COLOR = '#2a2a3a';

export default function AnomalyChart({ data }) {
  return (
    <div className={styles.card}>
      <h3>Anomalies Over Time (6h)</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data}>
          <defs>
            <filter id="lineGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="2.5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <CartesianGrid stroke={GRID_COLOR} strokeDasharray="3 3" />
          <XAxis dataKey="time_bucket" tick={{ fill: AXIS_COLOR, fontSize: 12 }} axisLine={{ stroke: GRID_COLOR }} tickLine={{ stroke: GRID_COLOR }} />
          <YAxis tick={{ fill: AXIS_COLOR, fontSize: 12 }} axisLine={{ stroke: GRID_COLOR }} tickLine={{ stroke: GRID_COLOR }} />
          <Tooltip
            contentStyle={{ background: '#1e1e2e', border: '1px solid #6366f1', borderRadius: '8px', color: '#f1f5f9' }}
            labelStyle={{ color: '#f1f5f9' }}
          />
          <Line type="monotone" dataKey="anomaly_count" stroke="#6366f1" strokeWidth={2.5} filter="url(#lineGlow)" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
