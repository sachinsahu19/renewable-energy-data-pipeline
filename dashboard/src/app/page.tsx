'use client';

import { useEffect, useState } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { Wind, Sun, Battery, Activity } from 'lucide-react';
import styles from './page.module.css';

interface TelemetryData {
  telemetry_hour: string;
  avg_wind_power_kw: number;
  avg_solar_power_kw: number;
  avg_battery_charge_kw: number;
  avg_total_power_kw: number;
}

export default function Dashboard() {
  const [data, setData] = useState<TelemetryData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/telemetry');
        const json = await res.json();
        
        // Reverse so chronological order is left to right
        const formattedData = json.reverse().map((d: any) => ({
          ...d,
          formattedTime: new Date(d.telemetry_hour).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }));
        
        setData(formattedData);
      } catch (e) {
        console.error("Failed to fetch data", e);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    // Refresh every 60 seconds
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        Loading Grid Telemetry...
      </div>
    );
  }

  const latest = data[data.length - 1] || {
    avg_total_power_kw: 0,
    avg_wind_power_kw: 0,
    avg_solar_power_kw: 0,
    avg_battery_charge_kw: 0
  };

  return (
    <main className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Renewable Energy Grid</h1>
          <p className={styles.subtitle}>Real-time Generation & Storage Telemetry</p>
        </div>
        <div className={styles.statusIndicator}>
          <div className={`${styles.statusDot} ${styles.pulse}`}></div>
          System Optimal
        </div>
      </div>

      <div className={styles.grid}>
        <div className={`${styles.glassPanel} ${styles.statCard}`}>
          <div className={styles.statHeader}>
            <div className={styles.statIcon} style={{ color: 'var(--color-total)' }}>
              <Activity size={24} />
            </div>
            Total Grid Output
          </div>
          <div className={styles.statValue}>
            {Math.round(latest.avg_total_power_kw).toLocaleString()}
            <span className={styles.statUnit}>kW</span>
          </div>
        </div>

        <div className={`${styles.glassPanel} ${styles.statCard}`}>
          <div className={styles.statHeader}>
            <div className={styles.statIcon} style={{ color: 'var(--color-wind)' }}>
              <Wind size={24} />
            </div>
            Wind Generation
          </div>
          <div className={styles.statValue}>
            {Math.round(latest.avg_wind_power_kw).toLocaleString()}
            <span className={styles.statUnit}>kW</span>
          </div>
        </div>

        <div className={`${styles.glassPanel} ${styles.statCard}`}>
          <div className={styles.statHeader}>
            <div className={styles.statIcon} style={{ color: 'var(--color-solar)' }}>
              <Sun size={24} />
            </div>
            Solar Generation
          </div>
          <div className={styles.statValue}>
            {Math.round(latest.avg_solar_power_kw).toLocaleString()}
            <span className={styles.statUnit}>kW</span>
          </div>
        </div>

        <div className={`${styles.glassPanel} ${styles.statCard}`}>
          <div className={styles.statHeader}>
            <div className={styles.statIcon} style={{ color: 'var(--color-battery)' }}>
              <Battery size={24} />
            </div>
            Battery Net Flow
          </div>
          <div className={styles.statValue}>
            {Math.round(latest.avg_battery_charge_kw).toLocaleString()}
            <span className={styles.statUnit}>kW</span>
          </div>
        </div>
      </div>

      <div className={`${styles.glassPanel} ${styles.chartContainer}`}>
        <h2 className={styles.chartHeader}>24-Hour Grid Performance</h2>
        <div className={styles.chartWrapper}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorWind" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--color-wind)" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="var(--color-wind)" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorSolar" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--color-solar)" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="var(--color-solar)" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorBattery" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--color-battery)" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="var(--color-battery)" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="formattedTime" stroke="var(--text-secondary)" tick={{fill: 'var(--text-secondary)'}} />
              <YAxis stroke="var(--text-secondary)" tick={{fill: 'var(--text-secondary)'}} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(22, 27, 34, 0.9)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#fff'
                }} 
              />
              <Legend verticalAlign="top" height={36}/>
              <Area type="monotone" name="Wind" dataKey="avg_wind_power_kw" stroke="var(--color-wind)" fillOpacity={1} fill="url(#colorWind)" />
              <Area type="monotone" name="Solar" dataKey="avg_solar_power_kw" stroke="var(--color-solar)" fillOpacity={1} fill="url(#colorSolar)" />
              <Area type="monotone" name="Battery" dataKey="avg_battery_charge_kw" stroke="var(--color-battery)" fillOpacity={1} fill="url(#colorBattery)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </main>
  );
}
