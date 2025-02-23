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
        print("last_90_data", last_90_data)
        return track_name, last_90_data

# --- New Helper Function ---
def find_spikes_from_parsed_data(spotify_data, tiktok_data):
    """
    Uses already parsed data (lists of [timestamp, value]) to compute spike intervals.
    Returns two lists of intervals (start_time, end_time) for Spotify and TikTok.
    """
    # Extract timestamps and values
    spotify_timestamps = [entry[0] for entry in spotify_data]
    tiktok_timestamps = [entry[0] for entry in tiktok_data]
    spotify_values = [entry[1] for entry in spotify_data]
    tiktok_values = [entry[1] for entry in tiktok_data]

    # Convert to datetime objects (epoch in ms)
    spotify_dates = pd.to_datetime(spotify_timestamps, unit='ms')
    tiktok_dates = pd.to_datetime(tiktok_timestamps, unit='ms')

    # Normalize values (simple normalization by dividing by max)
    spotify_series = pd.Series(spotify_values)
    tiktok_series = pd.Series(tiktok_values)
    spotify_normalized = spotify_series / spotify_series.max()
    tiktok_normalized = tiktok_series / tiktok_series.max()

    # Compute change over a 2-day window
    spotify_changes = spotify_normalized.diff(periods=2).dropna()
    tiktok_changes = tiktok_normalized.diff(periods=2).dropna()

    # Set thresholds (multipliers can be tuned)
    avg_spotify_change = spotify_changes.mean() + 3 * spotify_changes.std()
    avg_tiktok_change = tiktok_changes.mean() + 1 * tiktok_changes.std()

    # Identify spikes where derivative exceeds threshold
    spotify_spikes = spotify_changes[spotify_changes > avg_spotify_change]
    tiktok_spikes = tiktok_changes[tiktok_changes > avg_tiktok_change]

    # Build intervals: (start, end) using a 2-index window;
    # adjust index by subtracting 2 to approximate start times.
    spotify_spike_intervals = [
        (spotify_dates[i], spotify_dates[min(i + 2, len(spotify_dates) - 1)])
        for i in (spotify_spikes.index - 2) if i >= 0
    ]
    tiktok_spike_intervals = [
        (tiktok_dates[i], tiktok_dates[min(i + 2, len(tiktok_dates) - 1)])
        for i in (tiktok_spikes.index - 2) if i >= 0
    ]

    # Helper: merge overlapping intervals if needed
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

    spotify_spike_intervals = combine_intervals(spotify_spike_intervals)
    tiktok_spike_intervals = combine_intervals(tiktok_spike_intervals)
    return spotify_spike_intervals, tiktok_spike_intervals

# --- Spike Normalized Values & Plot Function Using Parsed Data ---

def get_spike_normalized_values(spotify_id: str, tiktok_id: str):
    """
    Returns two lists of tuples:
      For Spotify: (spike_start, spike_end, normalized_at_start, normalized_at_end)
      For TikTok: (spike_start, spike_end, normalized_at_start, normalized_at_end)
    Uses the parsed data only once.
    """
    spotify_info = get_spotify_reach_series(spotify_id)
    tiktok_info = get_tiktok_series(tiktok_id)
    if spotify_info is None or tiktok_info is None:
        print("Error fetching one or both data series.")
        return [], []
    # Use existing parsed data
    spotify_data = spotify_info[1]
    tiktok_data = tiktok_info[1]
    
    # Convert timestamps and values for normalization
    spotify_timestamps = [entry[0] for entry in spotify_data]
    spotify_values = [entry[1] for entry in spotify_data]
    tiktok_timestamps = [entry[0] for entry in tiktok_data]
    tiktok_values = [entry[1] for entry in tiktok_data]

    spotify_dates = pd.to_datetime(spotify_timestamps, unit='ms')
    tiktok_dates = pd.to_datetime(tiktok_timestamps, unit='ms')

    def min_max_normalize(values):
        min_val = min(values)
        max_val = max(values)
        return [(x - min_val) / (max_val - min_val) for x in values]

    spotify_normalized = min_max_normalize(spotify_values)
    tiktok_normalized = min_max_normalize(tiktok_values)

    # Use the new helper to get spike intervals from already parsed data
    spotify_spike_intervals, tiktok_spike_intervals = find_spikes_from_parsed_data(spotify_data, tiktok_data)

    # Helper to find the normalized value nearest to a target time
    def get_normalized_at_time(dates, norm_values, target):
        idx = min(range(len(dates)), key=lambda i: abs((dates[i] - target).total_seconds()))
        return norm_values[idx]

    spotify_spike_norm = []
    for start, end in spotify_spike_intervals:
        norm_start = get_normalized_at_time(spotify_dates, spotify_normalized, start)
        norm_end = get_normalized_at_time(spotify_dates, spotify_normalized, end)
        spotify_spike_norm.append((start, end, norm_start, norm_end))

    tiktok_spike_norm = []
    for start, end in tiktok_spike_intervals:
        norm_start = get_normalized_at_time(tiktok_dates, tiktok_normalized, start)
        norm_end = get_normalized_at_time(tiktok_dates, tiktok_normalized, end)
        tiktok_spike_norm.append((start, end, norm_start, norm_end))

    return spotify_spike_norm, tiktok_spike_norm

def plot_normalized_series_with_spikes(spotify_id: str, tiktok_id: str):
    """
    Plots the normalized Spotify (reach) and TikTok series with markers at the detected spike intervals.
    Uses the parsed data only once.
    """
    spotify_info = get_spotify_reach_series(spotify_id)
    tiktok_info = get_tiktok_series(tiktok_id)
    if spotify_info is None or tiktok_info is None:
        print("Error fetching one or both data series.")
        return
    spotify_data = spotify_info[1]
    tiktok_data = tiktok_info[1]
    song_name = spotify_info[0]
    
    spotify_timestamps = [entry[0] for entry in spotify_data]
    tiktok_timestamps = [entry[0] for entry in tiktok_data]
    spotify_values = [entry[1] for entry in spotify_data]
    tiktok_values = [entry[1] for entry in tiktok_data]

    spotify_dates = pd.to_datetime(spotify_timestamps, unit='ms')
    tiktok_dates = pd.to_datetime(tiktok_timestamps, unit='ms')

    def min_max_normalize(lst):
        min_val = min(lst)
        max_val = max(lst)
        return [(x - min_val) / (max_val - min_val) for x in lst]
    spotify_normalized = min_max_normalize(spotify_values)
    tiktok_normalized = min_max_normalize(tiktok_values)

    spotify_spikes, tiktok_spikes = find_spikes_from_parsed_data(spotify_data, tiktok_data)
    
    plt.figure(figsize=(10, 5))
    plt.plot(spotify_dates, spotify_normalized, label='Spotify (normalized)', color='blue')
    plt.plot(tiktok_dates, tiktok_normalized, label='TikTok (normalized)', color='red')

    # Mark spike start and end times
    for start, end in spotify_spikes:
        plt.axvline(x=start, color='blue', linestyle='--', alpha=0.7)
        plt.axvline(x=end, color='blue', linestyle='--', alpha=0.7)
    for start, end in tiktok_spikes:
        plt.axvline(x=start, color='red', linestyle='--', alpha=0.7)
        plt.axvline(x=end, color='red', linestyle='--', alpha=0.7)

    plt.xlabel('Date')
    plt.ylabel('Normalized Value')
    plt.title(f"Spotify and TikTok Series for {song_name}")
    plt.legend()
    plt.show()

# --- Example usage ---

if __name__ == "__main__":
    spotify_id = '2lmeytah'
    tiktok_id = '2lmeytah'
    
    # Plot the graphs with spikes
    plot_normalized_series_with_spikes(spotify_id, tiktok_id)
    
    # Get and print the normalized spike values (using the already parsed data)
    spotify_spike_values, tiktok_spike_values = get_spike_normalized_values(spotify_id, tiktok_id)
    print("\nSpotify Spike Normalized Values (start, end, norm_start, norm_end):")
    for spike in spotify_spike_values:
        print(spike)
    print("\nTikTok Spike Normalized Values (start, end, norm_start, norm_end):")
    for spike in tiktok_spike_values:
        print(spike)
# %%