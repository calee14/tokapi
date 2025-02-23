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
        min_val = min(lst)
        max_val = max(lst)
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

print(categorize_data('njtwgzci', 'njtwgzci'))