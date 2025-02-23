#%%
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

# ---------------------------
# STEP 1. Import the raw series data and prepare it for plotting
# ---------------------------
spotify_id = 'c7vi4fny'
tiktok_id = 'c7vi4fny'

# Get raw series (for plotting background time-series)
    # Retrieve series data
spotify_data = get_spotify_reach_series(spotify_id)[1]
song_name = get_spotify_reach_series(spotify_id)[0]
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

paired_spikes = []
for (start_spike, start_type, end_spike, end_type) in causation:
    if start_type == 'spotify' and end_type == 'tiktok':
        start_val = spotify_normalized.loc[spotify_dates == start_spike[0]].values[0]
        end_val = tiktok_normalized.loc[tiktok_dates == end_spike[0]].values[0]
        print("spotify > tiktok")
        print(f"start_val: {start_val}, end_val: {end_val}")
        plt.axvline(x=start_spike[0], color='blue', linestyle='--', alpha=0.5)
        plt.scatter([start_spike[0]], [start_val], color='blue', label='Spotify Critical Point' if start_spike == causation[0][0] else "")
        plt.axvline(x=end_spike[0], color='red', linestyle='--', alpha=0.5)
        plt.scatter([end_spike[0]], [end_val], color='red', label='TikTok Critical Point' if end_spike == causation[0][2] else "")
        # plt.axvspan(spotify_spike[0], tiktok_spike[0], color='green', alpha=0.3, label='Time Delta' if spotify_spike == causation[0][0] else "")
        paired_spikes.append((start_spike[0], end_spike[0], abs(end_spike[0] - start_spike[0]).days))
    elif start_type == 'tiktok' and end_type == 'spotify':
        start_val = tiktok_normalized.loc[tiktok_dates == start_spike[0]].values[0]
        end_val = spotify_normalized.loc[spotify_dates == end_spike[0]].values[0]
        print("tiktok > spotify")
        print(f"start_val: {start_val}, end_val: {end_val}")
        plt.axvline(x=start_spike[0], color='red', linestyle='--', alpha=0.5)
        plt.scatter([start_spike[0]], [start_val], color='red', label='TikTok Critical Point' if start_spike == causation[0][0] else "")
        plt.axvline(x=end_spike[0], color='blue', linestyle='--', alpha=0.5)
        plt.scatter([end_spike[0]], [end_val], color='blue', label='Spotify Critical Point' if end_spike == causation[0][2] else "")
        # plt.axvspan(tiktok_spike[0], spotify_spike[0], color='green', alpha=0.3, label='Time Delta' if tiktok_spike == causation[0][0] else "")
        paired_spikes.append((end_spike[0], start_spike[0], abs(start_spike[0] - end_spike[0]).days))

# ---------------------------
# STEP 4. Plot the time series and overlay the spike pairs with absolute delay annotations.
# ---------------------------

# Plot the background normalized time series for Spotify and TikTok
plt.plot(spotify_dates, spotify_normalized, label='Spotify (Reach)', color='blue', alpha=0.7)
plt.plot(spotify_dates, tiktok_normalized, label='TikTok', color='red', alpha=0.7)

# Format x-axis for dates
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

# Plot vertical lines (spike markers) and annotate the absolute delay for each paired spike.
for s_time, t_time, delay in paired_spikes:
    # Calculate midpoint between s_time and t_time for annotation
    mid_point = s_time + (t_time - s_time) / 2
    # Annotate the absolute delay value
    plt.annotate(f"{delay:.2f} days", xy=(mid_point, 0.5), xytext=(mid_point, 0.7),
                 arrowprops=dict(arrowstyle="->", color='black'),
                 ha='center', fontsize=10, color='black')

# Remove duplicate legend entries
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys())

plt.title(f"Absolute Time Delay Between Paired Spikes for {song_name}")
plt.xlabel("Date")
plt.ylabel("Normalized Value")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()