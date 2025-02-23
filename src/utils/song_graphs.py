#%%
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Data Retrieval Functions ---

def get_spotify_playlist_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data

def get_spotify_reach_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][1]['data'][-90:]
        return track_name, last_90_data

def get_tiktok_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=tiktok")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
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
        min_val = min(lst)
        max_val = max(lst)
        return [(x - min_val) / (max_val - min_val) for x in lst]
    spotify_normalized = pd.Series(min_max_normalize(spotify_series))
    tiktok_normalized = pd.Series(min_max_normalize(tiktok_series))

    # Calculate the change in normalized values every 2 days
    spotify_changes = spotify_normalized.diff(periods=2).dropna()
    tiktok_changes = tiktok_normalized.diff(periods=2).dropna()

    # Calculate the average of all 2-day derivatives
    avg_spotify_change = spotify_changes.mean() + spotify_changes.std() * 3
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
        min_val = min(lst)
        max_val = max(lst)
        return [(x - min_val) / (max_val - min_val) for x in lst]
    spotify_normalized = pd.Series(min_max_normalize(spotify_series))
    tiktok_normalized = pd.Series(min_max_normalize(tiktok_series))

    # Find spikes
    (spotify_spike_dates, spotify_spike_values), (tiktok_spike_dates, tiktok_spike_values) = find_spikes_in_normalized_series(spotify_id, tiktok_id)
    
    print("spotify_spikes", spotify_spike_dates)
    print("spotify_spike_values", spotify_spike_values)
    print("tiktok_spikes", tiktok_spike_dates)
    print("tiktok_spike_values", tiktok_spike_values)

    # Plotting both normalized series using actual dates on the x-axis
    plt.figure(figsize=(10, 5))
    plt.plot(spotify_dates, spotify_normalized, label='Spotify (normalized)')
    plt.plot(tiktok_dates, tiktok_normalized, label='TikTok (normalized)')

    # Add markers for spikes
    for (start, end), (start_val, end_val) in zip(spotify_spike_dates, spotify_spike_values):
        plt.axvline(x=start, color='blue', linestyle='--', alpha=0.5)
        plt.axvline(x=end, color='blue', linestyle='--', alpha=0.5)
        plt.scatter([start, end], [start_val, end_val], color='blue')

    for (start, end), (start_val, end_val) in zip(tiktok_spike_dates, tiktok_spike_values):
        plt.axvline(x=start, color='red', linestyle='--', alpha=0.5)
        plt.axvline(x=end, color='red', linestyle='--', alpha=0.5)
        plt.scatter([start, end], [start_val, end_val], color='red')

    plt.xlabel('Date')
    plt.ylabel('Normalized Value')
    plt.title(f"Spotify and TikTok Series for {song_name}")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    plot_normalized_series_with_spikes(spotify_id='2lmeytah', tiktok_id='2lmeytah')
# %%