import argparse
import os
import time
import uuid
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.getenv('SIMULATOR_DATA_DIR', '../data')
os.makedirs(DATA_DIR, exist_ok=True)

N_TURBINES = 10
N_PANELS = 20
N_BATTERIES = 5

TURBINE_IDS = [f'T-{str(i).zfill(3)}' for i in range(1, N_TURBINES + 1)]
PANEL_IDS = [f'P-{str(i).zfill(3)}' for i in range(1, N_PANELS + 1)]
BATTERY_IDS = [f'B-{str(i).zfill(3)}' for i in range(1, N_BATTERIES + 1)]

# State tracking for long-term patterns
turbine_state = {t_id: {'vibration_base': 1.0, 'cycles': 0} for t_id in TURBINE_IDS}
battery_state = {b_id: {'charge_pct': np.random.uniform(20, 80), 'cycles': int(np.random.uniform(10, 50))} for b_id in BATTERY_IDS}

# Make T-007 have a rising vibration pattern over time
FAILING_TURBINE = 'T-007'

def generate_wind_data(timestamp):
    records = []
    for t_id in TURBINE_IDS:
        # Base wind speed varies slowly over time, plus gusts
        hour_of_day = timestamp.hour
        base_wind = 10 + 5 * np.sin(hour_of_day * np.pi / 12) # Daily pattern
        wind_speed_mps = max(0, np.random.normal(base_wind, 2))
        
        # Power output cubic relation, cut in 3m/s, cut out 25m/s
        if 3 < wind_speed_mps < 25:
            power_output_kw = min(1500, 0.5 * 1.225 * (wind_speed_mps ** 3) * (np.pi * (40**2)) * 0.4 / 1000)
            blade_rpm = wind_speed_mps * 1.5 + np.random.normal(0, 1)
        else:
            power_output_kw = 0
            blade_rpm = 0
            
        # Vibration
        vib_mean = turbine_state[t_id]['vibration_base']
        if t_id == FAILING_TURBINE:
            # Increase base vibration slowly
            turbine_state[t_id]['vibration_base'] += 0.005
            
        vibration_mm_s = max(0, np.random.normal(vib_mean, 0.5))
        
        gearbox_temp_c = 40 + power_output_kw / 50 + np.random.normal(0, 2)
        
        status = 'OK'
        if vibration_mm_s > 10:
            status = 'FAULT'
        elif vibration_mm_s > 6:
            status = 'WARNING'
            
        # Dropouts (1% chance)
        if np.random.rand() < 0.01:
            power_output_kw = None
            
        records.append({
            'turbine_id': t_id,
            'timestamp': timestamp,
            'wind_speed_mps': wind_speed_mps,
            'blade_rpm': blade_rpm,
            'power_output_kw': power_output_kw,
            'vibration_mm_s': vibration_mm_s,
            'gearbox_temp_c': gearbox_temp_c,
            'status': status
        })
    return pd.DataFrame(records)


def generate_solar_data(timestamp):
    records = []
    hour = timestamp.hour
    minute = timestamp.minute
    time_val = hour + minute / 60
    
    # Parabola for irradiance peaking at 12:00, sunrise 6:00, sunset 18:00
    if 6 <= time_val <= 18:
        base_irradiance = max(0, -50 * (time_val - 12)**2 + 1000)
    else:
        base_irradiance = 0
        
    for p_id in PANEL_IDS:
        # Cloud cover noise
        irradiance_w_m2 = max(0, base_irradiance * np.random.uniform(0.7, 1.0))
        panel_temp_c = 15 + irradiance_w_m2 * 0.03 + np.random.normal(0, 1)
        
        # Power output
        power_output_kw = irradiance_w_m2 * 2 * 0.2 / 1000 # 2 sq meters, 20% efficiency
        
        inverter_status = 'OK'
        dc_voltage = 45 + np.random.normal(0, 2)
        
        # Occasional fault
        if np.random.rand() < 0.005:
            inverter_status = 'FAULT'
            dc_voltage = 0
            power_output_kw = 0
            
        records.append({
            'panel_id': p_id,
            'timestamp': timestamp,
            'irradiance_w_m2': irradiance_w_m2,
            'panel_temp_c': panel_temp_c,
            'power_output_kw': power_output_kw,
            'inverter_status': inverter_status,
            'dc_voltage': dc_voltage
        })
    return pd.DataFrame(records)


def generate_battery_data(timestamp, total_generation_kw):
    # Very simple simulation: charge during day, discharge at night
    records = []
    is_day = 8 <= timestamp.hour <= 18
    
    for b_id in BATTERY_IDS:
        state = battery_state[b_id]
        
        if is_day and state['charge_pct'] < 100:
            charge_rate_kw = np.random.uniform(10, 50)
        elif not is_day and state['charge_pct'] > 0:
            charge_rate_kw = -np.random.uniform(10, 30)
        else:
            charge_rate_kw = 0
            
        # Update charge state (assume rate is for 1 minute interval, total capacity 500kWh)
        delta_pct = (charge_rate_kw / 60) / 500 * 100
        state['charge_pct'] = max(0, min(100, state['charge_pct'] + delta_pct))
        
        if charge_rate_kw < 0 and state['charge_pct'] < 10: # arbitrary cycle count increment point
            if 'last_cycle' not in state or timestamp - state['last_cycle'] > timedelta(hours=12):
                state['cycles'] += 1
                state['last_cycle'] = timestamp
                
        temp_c = 25 + abs(charge_rate_kw) * 0.1 + np.random.normal(0, 1)
        
        records.append({
            'battery_id': b_id,
            'timestamp': timestamp,
            'charge_pct': state['charge_pct'],
            'charge_rate_kw': charge_rate_kw,
            'cycles_count': state['cycles'],
            'temp_c': temp_c
        })
    return pd.DataFrame(records)


def save_to_parquet(df, source_type, timestamp):
    if df.empty:
        return
        
    dt_str = timestamp.strftime('%Y-%m-%d')
    hour_str = timestamp.strftime('%H')
    
    # Save partitioned by date and hour to mimic S3 landing zone structure
    dir_path = os.path.join(DATA_DIR, 'raw', source_type, f'dt={dt_str}', f'hour={hour_str}')
    os.makedirs(dir_path, exist_ok=True)
    
    file_name = f"{uuid.uuid4()}.parquet"
    file_path = os.path.join(dir_path, file_name)
    df.to_parquet(file_path, index=False)


def run_simulation(start_time, end_time, step_seconds=60, sleep_time=0):
    current_time = start_time
    
    while current_time <= end_time:
        df_wind = generate_wind_data(current_time)
        df_solar = generate_solar_data(current_time)
        
        total_gen = df_wind['power_output_kw'].sum() + df_solar['power_output_kw'].sum()
        df_battery = generate_battery_data(current_time, total_gen)
        
        save_to_parquet(df_wind, 'wind_telemetry', current_time)
        save_to_parquet(df_solar, 'solar_telemetry', current_time)
        save_to_parquet(df_battery, 'battery_telemetry', current_time)
        
        print(f"[{current_time}] Generated telemetry data")
        current_time += timedelta(seconds=step_seconds)
        
        if sleep_time > 0:
            time.sleep(sleep_time)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Renewable Energy Telemetry Simulator')
    parser.add_argument('--backfill', type=int, help='Number of days to backfill')
    parser.add_argument('--stream', action='store_true', help='Stream continuously in real-time')
    
    args = parser.parse_args()
    
    if args.backfill:
        print(f"Starting backfill for {args.backfill} days...")
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=args.backfill)
        run_simulation(start_time, end_time, step_seconds=300) # 5 min intervals for backfill
        print("Backfill complete.")
        
    if args.stream:
        print("Starting real-time streaming...")
        while True:
            now = datetime.utcnow()
            run_simulation(now, now, step_seconds=60)
            time.sleep(60)
