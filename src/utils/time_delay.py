#%%
from song_graphs import (
    get_spotify_reach_series,
    get_tiktok_series,
    find_spikes_in_normalized_series
)
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# ---------------------------
# STEP 1. Import the raw series data and prepare it for plotting
# ---------------------------
spotify_id = 'njtwgzci'
tiktok_id = 'njtwgzci'

# Get raw series (for plotting background time-series)
spotify_info = get_spotify_reach_series(spotify_id)
tiktok_info = get_tiktok_series(tiktok_id)
if spotify_info is None or tiktok_info is None:
    print("Error fetching one or both data series.")
    exit()

song_name = spotify_info[0]

# Extract data
spotify_data = spotify_info[1]  # list of [timestamp, value]
tiktok_data = tiktok_info[1]

# Create pandas DataFrames for time series
df_spotify = pd.DataFrame(spotify_data, columns=['timestamp', 'value'])
df_spotify['date'] = pd.to_datetime(df_spotify['timestamp'], unit='ms')
df_tiktok = pd.DataFrame(tiktok_data, columns=['timestamp', 'value'])
df_tiktok['date'] = pd.to_datetime(df_tiktok['timestamp'], unit='ms')

# Normalize the values for plotting (min-max normalization)
df_spotify['normalized'] = (df_spotify['value'] - df_spotify['value'].min()) / (df_spotify['value'].max() - df_spotify['value'].min())
df_tiktok['normalized'] = (df_tiktok['value'] - df_tiktok['value'].min()) / (df_tiktok['value'].max() - df_tiktok['value'].min())

# ---------------------------
# STEP 2. Retrieve spike intervals and normalized spike values
# ---------------------------
# find_spikes_in_normalized_series returns a tuple:
# ((spotify_spike_dates, spotify_spike_values), (tiktok_spike_dates, tiktok_spike_values))
(spi_intervals, spi_norm_values), (tti_intervals, tti_norm_values) = find_spikes_in_normalized_series(spotify_id, tiktok_id)

# ---------------------------
# STEP 3. Pair the spikes to compute the time delays (using absolute delay)
# ---------------------------
# Extract the start timestamps from each spike interval
spotify_start_times = [interval[0] for interval in spi_intervals]
tiktok_start_times = [interval[0] for interval in tti_intervals]

# Copy available Spotify spike start times so each is only paired once
available_spotify = spotify_start_times.copy()

paired_spikes = []  # Each element is (TikTok spike start, Spotify spike start, absolute delay in days)
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

print("Paired spikes (TikTok spike start, Spotify spike start, absolute time delay in days):")
for pair in paired_spikes:
    print(pair)

# ---------------------------
# STEP 4. Plot the time series and overlay the spike pairs with absolute delay annotations.
# ---------------------------
fig, ax = plt.subplots(figsize=(12, 6))

# Plot the background normalized time series for Spotify and TikTok
ax.plot(df_spotify['date'], df_spotify['normalized'], label='Spotify (Reach)', color='blue', alpha=0.7)
ax.plot(df_tiktok['date'], df_tiktok['normalized'], label='TikTok', color='red', alpha=0.7)

# Format x-axis for dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.AutoDateLocator())

# Plot vertical lines (spike markers) and annotate the absolute delay for each paired spike.
for t_time, s_time, delay in paired_spikes:
    # Plot spike markers as vertical lines
    ax.axvline(t_time, color='red', linestyle='--', alpha=0.8, label='TikTok Spike')
    ax.axvline(s_time, color='blue', linestyle='--', alpha=0.8, label='Spotify Spike')
    
    # Calculate midpoint between t_time and s_time for annotation
    mid_point = t_time + (s_time - t_time) / 2
    # Annotate the absolute delay value
    ax.annotate(f"{delay:.2f} days", xy=(mid_point, 0.5), xytext=(mid_point, 0.7),
                arrowprops=dict(arrowstyle="->", color='black'),
                ha='center', fontsize=10, color='black')

# Remove duplicate legend entries
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys())

ax.set_title(f"Absolute Time Delay Between Paired Spikes for {song_name}")
ax.set_xlabel("Date")
ax.set_ylabel("Normalized Value")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()