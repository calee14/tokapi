import os
from datetime import datetime
import pandas as pd
import statistics

from song_graphs import (
    get_spotify_reach_series,
    get_tiktok_series,
    find_spikes_in_normalized_series,
    determine_causation
)

def parse_tiktok_series_csv(file_id):
    # Construct file name and full file path
    file_name = f"tiktok_series_{file_id}.csv"
    file_path = os.path.join('tiktok_series_dataset', file_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        
        if len(lines) < 3:
            raise ValueError("CSV file does not have the expected structure.")
        
        # Extract components based on file structure
        playlist_title = lines[0]
        artist = lines[-2]
        image_url = lines[-1]
        
        # Data rows are assumed to be between the first and the last two lines
        data_lines = lines[1:-2]
        data = []
        for line in data_lines:
            parts = line.split(',')
            if len(parts) == 2:
                try:
                    timestamp = int(parts[0])
                    value = int(parts[1])
                    data.append((timestamp, value))
                except ValueError:
                    print(f"Skipping invalid data row: {line}")
            else:
                print(f"Skipping line with unexpected format: {line}")
        
        # Convert data rows to a DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'value'])
        
        return {
            0: playlist_title,
            1: df,
            2: artist,
            3: image_url
        }
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def parse_spotify_reach_csv(file_id):
    # Construct file name and full file path
    file_name = f"spotify_reach_series_{file_id}.csv"
    file_path = os.path.join('spotify_reach_dataset', file_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        
        if len(lines) < 3:
            raise ValueError("CSV file does not have the expected structure.")
        
        # Extract components based on file structure
        playlist_title = lines[0]
        artist = lines[-2]
        image_url = lines[-1]
        
        # Data rows are assumed to be between the first and the last two lines
        data_lines = lines[1:-2]
        data = []
        for line in data_lines:
            parts = line.split(',')
            if len(parts) == 2:
                try:
                    timestamp = int(parts[0])
                    value = int(parts[1])
                    data.append((timestamp, value))
                except ValueError:
                    print(f"Skipping invalid data row: {line}")
            else:
                print(f"Skipping line with unexpected format: {line}")
        
        # Convert data rows to a DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'value'])
        
        return {
            0: playlist_title,
            1: df,
            2: artist,
            3: image_url
        }
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def categorize_data(spotify_id: str, tiktok_id: str):
    spotify_data = get_spotify_reach_series(spotify_id)[1]
    tiktok_data = get_tiktok_series(tiktok_id)[1]

    if spotify_data is None or tiktok_data is None:
        print("Error fetching one or both data series.")

    # Extract timestamps and values (assumes [timestamp, value] structure)
    spotify_timestamps = [entry[0] for entry in spotify_data]
    tiktok_timestamps = [entry[0] for entry in tiktok_data]
    spotify_values = [entry[1] for entry in spotify_data]
    tiktok_values = [entry[1] for entry in tiktok_data]

    # Convert timestamps to datetime objects (assuming epoch in ms)
    spotify_dates = pd.to_datetime(spotify_timestamps, unit='ms')
    tiktok_dates = pd.to_datetime(tiktok_timestamps, unit='ms')

    # Normalize the values
    def min_max_normalize(lst):
        if not lst:
            return []
        min_val = min(lst)
        max_val = max(lst)
        # Adding a small constant to avoid division by zero
        return [(x - min_val) / (max_val - min_val + 1e-8) for x in lst]

    spotify_normalized = min_max_normalize(spotify_values)
    tiktok_normalized = min_max_normalize(tiktok_values)

    # Find spikes
    (spotify_spike_dates, spotify_spike_values), (tiktok_spike_dates, tiktok_spike_values) = find_spikes_in_normalized_series(spotify_id, tiktok_id)

    causation = determine_causation(spotify_spike_dates, tiktok_spike_dates)
    
    spotify_first = []
    tiktok_first = []
    
    for (start_spike, start_type, end_spike, end_type) in causation:
        if start_type == 'spotify':
            start_val = next(v for d, v in zip(spotify_dates, spotify_normalized) if d == start_spike[0])
            end_val = next(v for d, v in zip(tiktok_dates, tiktok_normalized) if d == end_spike[1])
            tiktok_change = end_val - next(v for d, v in zip(tiktok_dates, tiktok_normalized) if d == end_spike[0])
            spotify_change = next(v for d, v in zip(spotify_dates, spotify_normalized) if d == start_spike[1]) - start_val
            spotify_first.append((tiktok_change / spotify_change, abs((end_spike[0] - start_spike[0]).days)))
        else:
            start_val = next(v for d, v in zip(tiktok_dates, tiktok_normalized) if d == start_spike[0])
            end_val = next(v for d, v in zip(spotify_dates, spotify_normalized) if d == end_spike[1])
            spotify_change = end_val - next(v for d, v in zip(spotify_dates, spotify_normalized) if d == end_spike[0])
            tiktok_change = next(v for d, v in zip(tiktok_dates, tiktok_normalized) if d == start_spike[1]) - start_val
            tiktok_first.append((spotify_change / tiktok_change, abs((start_spike[0] - end_spike[0]).days)))
            
    return spotify_first, tiktok_first

# Calculate averages and standard deviations over all songs
current_dir = os.path.dirname(os.path.abspath(__file__))
songs_file_path = os.path.join(current_dir, "songs")

with open(songs_file_path) as file:
    codes = file.read().splitlines()

spot_delay_values = []
tik_delay_values = []
spot_coef_values = []
tik_coef_values = []

for code in codes:
    all_data = categorize_data(code, code)
    # all_data[0] corresponds to cases where Spotify spiked first,
    # and all_data[1] corresponds to cases where TikTok spiked first.
    for (coef, delay) in all_data[0]:
        spot_coef_values.append(coef)
        spot_delay_values.append(delay)
    for (coef, delay) in all_data[1]:
        tik_coef_values.append(coef)
        tik_delay_values.append(delay)

# Compute averages and standard deviations
avg_spot_delay = sum(spot_delay_values) / len(spot_delay_values) if spot_delay_values else 0
std_spot_delay = statistics.stdev(spot_delay_values) if len(spot_delay_values) > 1 else 0

avg_tik_delay = sum(tik_delay_values) / len(tik_delay_values) if tik_delay_values else 0
std_tik_delay = statistics.stdev(tik_delay_values) if len(tik_delay_values) > 1 else 0

avg_spot_coef = sum(spot_coef_values) / len(spot_coef_values) if spot_coef_values else 0
std_spot_coef = statistics.stdev(spot_coef_values) if len(spot_coef_values) > 1 else 0

avg_tik_coef = sum(tik_coef_values) / len(tik_coef_values) if tik_coef_values else 0
std_tik_coef = statistics.stdev(tik_coef_values) if len(tik_coef_values) > 1 else 0

print('Spotify Average Time Delay:', avg_spot_delay)
print('Spotify Time Delay Standard Deviation:', std_spot_delay)
print('TikTok Average Time Delay:', avg_tik_delay)
print('TikTok Time Delay Standard Deviation:', std_tik_delay)

print('Spotify Average Coef:', avg_spot_coef)
print('Spotify Coef Standard Deviation:', std_spot_coef)
print('TikTok Average Coef:', avg_tik_coef)
print('TikTok Coef Standard Deviation:', std_tik_coef)