from song_graphs import (
    get_spotify_reach_series,
    get_tiktok_series,
    find_spikes_in_normalized_series,
    determine_causation
)
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os

def parse_tiktok_series_csv(file_id):
    # Construct file name and full file path
    file_name = f"tiktok_series_{file_id}.csv"
    file_path = os.path.join('tiktok_series_dataset', file_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        
        if len(lines) < 3:
            raise ValueError("CSV file does not have the expected structure.")
        
        # Extract the components based on the assumed file structure
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
        
        # Extract the components based on the assumed file structure
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

    # Create pandas DataFrames for time series
    # Convert timestamps to datetime objects (assuming epoch in ms)
    spotify_dates = pd.to_datetime(spotify_timestamps, unit='ms')
    tiktok_dates = pd.to_datetime(tiktok_timestamps, unit='ms')

    # Normalize the values
    spotify_series = pd.Series(spotify_values)
    tiktok_series = pd.Series(tiktok_values)
    def min_max_normalize(lst):
        min_val = min(lst) if len(lst) else 0 
        max_val = max(lst) if len(lst) else 0
        return [(x - min_val) / (max_val - min_val + pow(1, -8)) for x in lst] # check for division by 0
    spotify_normalized = pd.Series(min_max_normalize(spotify_series))
    tiktok_normalized = pd.Series(min_max_normalize(tiktok_series))

    # Find spikes
    (spotify_spike_dates, spotify_spike_values), (tiktok_spike_dates, tiktok_spike_values) = find_spikes_in_normalized_series(spotify_id, tiktok_id)

    causation = determine_causation(spotify_spike_dates, tiktok_spike_dates)
    
    spotify_first = []
    tiktok_first = []
    
    for (start_spike, start_type, end_spike, end_type) in causation:
        if start_type == 'spotify':
            start_val = spotify_normalized.loc[spotify_dates == start_spike[0]].values[0]
            end_val = tiktok_normalized.loc[tiktok_dates == end_spike[1]].values[0]
            tiktok_change = end_val - tiktok_normalized.loc[tiktok_dates == end_spike[0]].values[0]
            spotify_change = spotify_normalized.loc[spotify_dates == start_spike[1]].values[0] - start_val
            spotify_first.append((tiktok_change / spotify_change, abs(end_spike[0] - start_spike[0]).days))
        else:
            start_val = tiktok_normalized.loc[tiktok_dates == start_spike[0]].values[0]
            end_val = spotify_normalized.loc[spotify_dates == end_spike[1]].values[0]
            spotify_change = end_val - spotify_normalized.loc[spotify_dates == end_spike[0]].values[0]
            tiktok_change = tiktok_normalized.loc[tiktok_dates == start_spike[1]].values[0] - start_val
            tiktok_first.append((spotify_change / tiktok_change, abs(start_spike[0] - end_spike[0]).days))
            
    return spotify_first, tiktok_first

#print(categorize_data('o6czgimx', 'o6czgimx'))


with open("src/utils/songs") as file:
    codes = file.read().splitlines()

total_delay_spot = 0
count_spot = 0

for code in codes:
    all_data = categorize_data(code, code)
    for i in range(len(all_data[0])):
        time_delay = all_data[0][i][1]
        total_delay_spot = total_delay_spot + time_delay
        count_spot = count_spot + 1

print('Spotify Average Time Delay:', total_delay_spot/count_spot)

total_delay_tik = 0
count_tik = 0

for code in codes:
    all_data = categorize_data(code, code)
    for i in range(len(all_data[1])):
        time_delay = all_data[1][i][1]
        total_delay_tik = total_delay_tik + time_delay
        count_tik = count_tik + 1

print('Tiktok Average Time Delay:', total_delay_tik/count_tik)

total_coef_spot = 0
count_spot_1 = 0

for code in codes:
    all_data = categorize_data(code, code)
    for i in range(len(all_data[0])):
        coef = all_data[0][i][0]
        total_coef_spot = total_coef_spot + coef
        count_spot_1 = count_spot_1 + 1

print('Spotify Average Coef:', total_coef_spot/count_spot_1)

total_coef_tik = 0
count_tik_1 = 0

for code in codes:
    all_data = categorize_data(code, code)
    for i in range(len(all_data[1])):
        coef = all_data[1][i][0]
        total_coef_tik = total_coef_tik + coef
        count_tik_1 = count_tik_1 + 1

print('Tiktok Average Coef:', total_coef_tik/count_tik_1)