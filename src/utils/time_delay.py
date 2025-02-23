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
spotify_id = 'bjux4okf'
tiktok_id = 'bjux4okf'

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

causation = determine_causation(spi_intervals, tti_intervals)

paired_spikes = []
for (spotify_spike, spotify_type, tiktok_spike, tiktok_type) in causation:
    if spotify_type == 'spotify' and tiktok_type == 'tiktok':
        start_val = df_spotify['normalized'].loc[df_spotify['date'] == spotify_spike[0]].values[0]
        end_val = df_tiktok['normalized'].loc[df_tiktok['date'] == tiktok_spike[0]].values[0]
        plt.axvline(x=spotify_spike[0], color='blue', linestyle='--', alpha=0.5)
        plt.scatter([spotify_spike[0]], [start_val], color='blue', label='Spotify Critical Point' if spotify_spike == causation[0][0] else "")
        plt.axvline(x=tiktok_spike[0], color='red', linestyle='--', alpha=0.5)
        plt.scatter([tiktok_spike[0]], [end_val], color='red', label='TikTok Critical Point' if tiktok_spike == causation[0][2] else "")
        # plt.axvspan(spotify_spike[0], tiktok_spike[0], color='green', alpha=0.3, label='Time Delta' if spotify_spike == causation[0][0] else "")
        paired_spikes.append((spotify_spike[0], tiktok_spike[0], abs(tiktok_spike[0] - spotify_spike[0]).days))
    elif spotify_type == 'tiktok' and tiktok_type == 'spotify':
        start_val = df_tiktok['normalized'].loc[df_tiktok['date'] == tiktok_spike[0]].values[0]
        end_val = df_spotify['normalized'].loc[df_spotify['date'] == spotify_spike[0]].values[0]
        plt.axvline(x=tiktok_spike[0], color='red', linestyle='--', alpha=0.5)
        plt.scatter([tiktok_spike[0]], [start_val], color='red', label='TikTok Critical Point' if tiktok_spike == causation[0][0] else "")
        plt.axvline(x=spotify_spike[0], color='blue', linestyle='--', alpha=0.5)
        plt.scatter([spotify_spike[0]], [end_val], color='blue', label='Spotify Critical Point' if spotify_spike == causation[0][2] else "")
        # plt.axvspan(tiktok_spike[0], spotify_spike[0], color='green', alpha=0.3, label='Time Delta' if tiktok_spike == causation[0][0] else "")
        paired_spikes.append((tiktok_spike[0], spotify_spike[0], abs(spotify_spike[0] - tiktok_spike[0]).days))

# ---------------------------
# STEP 4. Plot the time series and overlay the spike pairs with absolute delay annotations.
# ---------------------------

# Plot the background normalized time series for Spotify and TikTok
plt.plot(df_spotify['date'], df_spotify['normalized'], label='Spotify (Reach)', color='blue', alpha=0.7)
plt.plot(df_tiktok['date'], df_tiktok['normalized'], label='TikTok', color='red', alpha=0.7)

# Format x-axis for dates
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

# Plot vertical lines (spike markers) and annotate the absolute delay for each paired spike.
for s_time, t_time, delay in paired_spikes:
    # Plot spike markers as vertical lines
    plt.axvline(s_time, color='blue', linestyle='--', alpha=0.8, label='Spotify Spike')
    plt.axvline(t_time, color='red', linestyle='--', alpha=0.8, label='TikTok Spike')
    
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