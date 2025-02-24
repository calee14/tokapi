#%%
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

# MIN_EPOCH_SEC = 1732406400  # minimum epoch time in seconds
# MIN_EPOCH_MS = MIN_EPOCH_SEC * 1000  # convert to milliseconds

def get_spotify_playlist_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:] if len(parsed_data['chart']['seriesData'][0]['data']) >= 90 else parsed_data['chart']['seriesData'][0]['data'][len(parsed_data['chart']['seriesData'][0]['data']):]
        return track_name, last_90_data

def get_spotify_reach_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:] if len(parsed_data['chart']['seriesData'][0]['data']) >= 90 else parsed_data['chart']['seriesData'][0]['data'][len(parsed_data['chart']['seriesData'][0]['data']):]
        return track_name, last_90_data

def get_tiktok_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=tiktok")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:] if len(parsed_data['chart']['seriesData'][0]['data']) >= 90 else parsed_data['chart']['seriesData'][0]['data'][len(parsed_data['chart']['seriesData'][0]['data']):]
        return track_name, last_90_data

def find_spikes_in_normalized_series(spotify_id: str, tiktok_id: str):
    # Retrieve series data
    spotify_data = get_spotify_reach_series(spotify_id)[1]
    tiktok_data = get_tiktok_series(tiktok_id)[1]

    if spotify_data is None or tiktok_data is None:
        print("Error fetching one or both data series.")
        return [], []

    # Extract timestamps and values (assumes [timestamp, value] structure)
    spotify_timestamps = [entry[0] for entry in spotify_data]
    tiktok_timestamps = [entry[0] for entry in tiktok_data]
    spotify_values = [entry[1] for entry in spotify_data]
    tiktok_values = [entry[1] for entry in tiktok_data]

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

    # Calculate the change in normalized values every 2 days
    spotify_changes = spotify_normalized.diff(periods=2).dropna()
    tiktok_changes = tiktok_normalized.diff(periods=2).dropna()

    # Calculate the average of all 2-day derivatives
    avg_spotify_change = spotify_changes.mean() + spotify_changes.std()
    avg_tiktok_change = tiktok_changes.mean() + tiktok_changes.std()

    # Identify spikes where the 2-day derivative is greater than the average
    spotify_spikes = spotify_changes[spotify_changes > avg_spotify_change]
    tiktok_spikes = tiktok_changes[tiktok_changes > avg_tiktok_change]

    # Create a list of tuples representing the spikes
    spotify_spike_dates = [(spotify_dates[i], spotify_dates[min(i + 2, len(spotify_dates) - 1)]) for i in spotify_spikes.index - 2]
    tiktok_spike_dates = [(tiktok_dates[i], tiktok_dates[min(i + 2, len(tiktok_dates) - 1)]) for i in tiktok_spikes.index - 2]

    # Function to combine overlapping intervals
    def combine_intervals(intervals):
        if not intervals:
            return intervals
        intervals.sort()
        combined = [intervals[0]]
        for current in intervals[1:]:
            last = combined[-1]
            if current[0] <= last[1]:
                combined[-1] = (last[0], max(last[1], current[1]))
            else:
                combined.append(current)
        return combined

    # Combine overlapping intervals
    spotify_spike_dates = combine_intervals(spotify_spike_dates)
    tiktok_spike_dates = combine_intervals(tiktok_spike_dates)

    # Get the normalized values for each spike
    spotify_spike_values = [(spotify_normalized.loc[spotify_dates == start].values[0], spotify_normalized.loc[spotify_dates == end].values[0]) for start, end in spotify_spike_dates]
    tiktok_spike_values = [(tiktok_normalized.loc[tiktok_dates == start].values[0], tiktok_normalized.loc[tiktok_dates == end].values[0]) for start, end in tiktok_spike_dates]

    return (spotify_spike_dates, spotify_spike_values), (tiktok_spike_dates, tiktok_spike_values)

def determine_causation(spotify_spikes, tiktok_spikes):
    causation = []
    all_spikes = [(date, 'spotify') for date in spotify_spikes] + [(date, 'tiktok') for date in tiktok_spikes]
    all_spikes.sort()

    used_times = set()

    for i in range(len(all_spikes) - 1):
        current_spike, current_type = all_spikes[i]
        next_spike, next_type = all_spikes[i + 1]

        if current_spike[0] in used_times or next_spike[0] in used_times:
            continue

        if next_spike[0] <= current_spike[1] + pd.Timedelta(days=20):
            if current_type == 'spotify' and next_type == 'tiktok':
                causation.append((current_spike, 'spotify', next_spike, 'tiktok'))
                used_times.add(current_spike[0])
                used_times.add(next_spike[0])
            elif current_type == 'tiktok' and next_type == 'spotify':
                causation.append((current_spike, 'tiktok', next_spike, 'spotify'))
                used_times.add(current_spike[0])
                used_times.add(next_spike[0])

    return causation

def plot_normalized_series_with_spikes(spotify_id: str, tiktok_id: str):
    # Retrieve series data
    spotify_data = get_spotify_reach_series(spotify_id)[1]
    song_name = get_spotify_reach_series(spotify_id)[0]
    tiktok_data = get_tiktok_series(tiktok_id)[1]

    if spotify_data is None or tiktok_data is None:
        print("Error fetching one or both data series.")
        return

    # Extract timestamps and values (assumes [timestamp, value] structure)
    spotify_timestamps = [entry[0] for entry in spotify_data]
    tiktok_timestamps = [entry[0] for entry in tiktok_data]
    spotify_values = [entry[1] for entry in spotify_data]
    tiktok_values = [entry[1] for entry in tiktok_data]

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
    
    print("spotify_spikes", spotify_spike_dates)
    print("spotify_spike_values", spotify_spike_values)
    print("tiktok_spikes", tiktok_spike_dates)
    print("tiktok_spike_values", tiktok_spike_values)

    # Determine causation
    causation = determine_causation(spotify_spike_dates, tiktok_spike_dates)
    print("causation", causation)
    
    # Plotting both normalized series using actual dates on the x-axis
    plt.figure(figsize=(10, 5))
    plt.plot(spotify_dates, spotify_normalized, label='Spotify (normalized)')
    plt.plot(tiktok_dates, tiktok_normalized, label='TikTok (normalized)')

    # Add markers for causation spikes and shade the causation areas
    for (spotify_spike, spotify_type, tiktok_spike, tiktok_type) in causation:
        if spotify_type == 'spotify' and tiktok_type == 'tiktok':
            start_val = spotify_normalized.loc[spotify_dates == spotify_spike[0]].values[0]
            end_val = tiktok_normalized.loc[tiktok_dates == tiktok_spike[1]].values[0]
            plt.axvline(x=spotify_spike[0], color='blue', linestyle='--', alpha=0.5)
            plt.scatter([spotify_spike[0]], [start_val], color='blue', label='Spotify Critical Point' if spotify_spike == causation[0][0] else "")
            plt.axvline(x=tiktok_spike[1], color='red', linestyle='--', alpha=0.5)
            plt.scatter([tiktok_spike[1]], [end_val], color='red', label='TikTok Critical Point' if tiktok_spike == causation[0][2] else "")
            plt.axvspan(spotify_spike[0], tiktok_spike[1], color='green', alpha=0.3, label='Time Delta' if spotify_spike == causation[0][0] else "")
        elif spotify_type == 'tiktok' and tiktok_type == 'spotify':
            start_val = tiktok_normalized.loc[tiktok_dates == spotify_spike[0]].values[0]
            end_val = spotify_normalized.loc[spotify_dates == tiktok_spike[1]].values[0]
            plt.axvline(x=spotify_spike[0], color='red', linestyle='--', alpha=0.5)
            plt.scatter([spotify_spike[0]], [start_val], color='red', label='TikTok Critical Point' if spotify_spike == causation[0][0] else "")
            plt.axvline(x=tiktok_spike[1], color='blue', linestyle='--', alpha=0.5)
            plt.scatter([tiktok_spike[1]], [end_val], color='blue', label='Spotify Critical Point' if tiktok_spike == causation[0][2] else "")
            plt.axvspan(spotify_spike[0], tiktok_spike[1], color='green', alpha=0.3, label='Time Delta' if spotify_spike == causation[0][0] else "")

    plt.xlabel('Date')
    plt.ylabel('Normalized Value')
    plt.title(f"Spotify and TikTok Series for {song_name}")
    plt.legend()
    plt.show()

'''
# Example usage:
if __name__ == "__main__":
    plot_normalized_series_with_spikes(spotify_id='njtwgzci', tiktok_id='njtwgzci')
'''
# %%

def pair_spikes(spotify_id, tiktok_id):
    """
    Retrieve spike intervals from Spotify and TikTok data, pair the spikes based on their start times,
    and compute the absolute delay (in days) for each pair.
    
    Parameters:
        spotify_id (str): The Spotify ID for the song.
        tiktok_id (str): The TikTok ID for the song.
        
    Returns:
        list of tuples: Each tuple contains:
            (tiktok_spike_start (datetime), spotify_spike_start (datetime), delay_days (float))
    """
    # Retrieve spike intervals and normalized spike values
    (spi_intervals, spi_norm_values), (tti_intervals, tti_norm_values) = find_spikes_in_normalized_series(spotify_id, tiktok_id)
    
    # Extract the start timestamps from each spike interval
    spotify_start_times = [interval[0] for interval in spi_intervals]
    tiktok_start_times = [interval[0] for interval in tti_intervals]
    
    # Copy available Spotify spike start times so each is only paired once
    available_spotify = spotify_start_times.copy()
    
    paired_spikes = []  # Each element: (TikTok spike start, Spotify spike start, absolute delay in days)
    for t_time in tiktok_start_times:
        nearest_spotify = None
        min_diff = None
        for s_time in available_spotify:
            diff = abs((s_time - t_time).total_seconds())
            if min_diff is None or diff < min_diff:
                min_diff = diff
                nearest_spotify = s_time
        if nearest_spotify is not None:
            # Compute absolute delay in days
            delay_days = abs((nearest_spotify - t_time).total_seconds()) / 86400.0
            paired_spikes.append((t_time, nearest_spotify, delay_days))
            available_spotify.remove(nearest_spotify)
    
    return paired_spikes

'''
# Example usage:
paired_spikes = pair_spikes(spotify_id = 'njtwgzci', tiktok_id = 'njtwgzci')
print("Paired spikes (TikTok spike start, Spotify spike start, absolute time delay in days):")
for pair in paired_spikes:
    if pair[2] < 20:
        print(pair)
'''

with open("songs", "r") as file:
    codes = file.read().splitlines()
    print(codes)

total_days = 0

for code in codes:
    series = get_spotify_reach_series(code)[1]
    series2 = get_tiktok_series(code)[1]
    if not (series and series2):
        continue
    paired_spikes = pair_spikes(code, code)
    for pair in paired_spikes:
        if pair[2] < 20:
            print(pair)
            total_days = pair[2] + total_days
            print(total_days)

avg_days = total_days/len(codes)
print('avg_days', avg_days)