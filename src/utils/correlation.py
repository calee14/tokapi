#%%
from .song_graphs import (
    get_spotify_reach_series,
    get_tiktok_series,
    find_spikes_in_normalized_series
)
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def get_correlation_coefficients(spotify_id: str, tiktok_id: str):
    """
    Pairs each TikTok spike (using its start time) with the nearest unpaired Spotify spike (by start time).
    For each paired spike, computes the jump magnitude (normalized_end - normalized_start) for both platforms,
    and then calculates the correlation coefficient as:
       
           (tiktok_jump_magnitude / spotify_jump_magnitude)
    
    Returns:
        A list of tuples: (tiktok_spike_start, tiktok_spike_end, spotify_spike_start, spotify_spike_end, correlation_coefficient)
    """
    # Retrieve spike data from the parsed series.
    # Each spike date is a tuple: (start, end)
    # Each spike value is a tuple: (norm_start, norm_end)
    (spotify_spike_dates, spotify_spike_values), (tiktok_spike_dates, tiktok_spike_values) = \
        find_spikes_in_normalized_series(spotify_id, tiktok_id)
    
    available_spotify = spotify_spike_dates.copy()
    correlations = []
    
    for idx, t_interval in enumerate(tiktok_spike_dates):
        t_start, t_end = t_interval
        t_norm_start, t_norm_end = tiktok_spike_values[idx]
        nearest_spotify = None
        min_diff = None
        for s_interval in available_spotify:
            s_start, s_end = s_interval
            diff = abs((s_start - t_start).total_seconds())
            if min_diff is None or diff < min_diff:
                min_diff = diff
                nearest_spotify = s_interval
        if nearest_spotify is not None:
            available_spotify.remove(nearest_spotify)
            s_idx = spotify_spike_dates.index(nearest_spotify)
            s_norm_start, s_norm_end = spotify_spike_values[s_idx]
            # Calculate jump magnitudes for both spikes
            t_jump = t_norm_end - t_norm_start
            s_jump = s_norm_end - s_norm_start
            if s_jump != 0:
                coefficient = t_jump / s_jump
                # Return full spike intervals for TikTok and Spotify along with the coefficient.
                correlations.append((t_start, t_end, nearest_spotify[0], nearest_spotify[1], coefficient))
                
    return correlations

# --- Plotting Function for Correlation Coefficients ---
def plot_correlation_coefficients(spotify_id: str, tiktok_id: str):
    """
    Plots the normalized time-series for Spotify (reach) and TikTok,
    overlays the detected spike markers (both spike starts and ends), and annotates each paired spike
    with the correlation coefficient computed as (tiktok_jump / spotify_jump). The spike start markers
    are plotted as dashed vertical lines, while the spike end markers are shown as ".-" vertical lines.
    """
    # Retrieve raw series data for background plotting.
    spotify_info = get_spotify_reach_series(spotify_id)
    tiktok_info = get_tiktok_series(tiktok_id)
    if spotify_info is None or tiktok_info is None:
        print("Error fetching one or both data series.")
        return
    
    song_name = spotify_info[0]
    spotify_data = spotify_info[1]  # list of [timestamp, value]
    tiktok_data = tiktok_info[1]
    
    # Create DataFrames and compute normalized values (min-max normalization).
    df_spotify = pd.DataFrame(spotify_data, columns=['timestamp', 'value'])
    df_spotify['date'] = pd.to_datetime(df_spotify['timestamp'], unit='ms')
    df_spotify['normalized'] = (df_spotify['value'] - df_spotify['value'].min()) / (df_spotify['value'].max() - df_spotify['value'].min())
    
    df_tiktok = pd.DataFrame(tiktok_data, columns=['timestamp', 'value'])
    df_tiktok['date'] = pd.to_datetime(df_tiktok['timestamp'], unit='ms')
    df_tiktok['normalized'] = (df_tiktok['value'] - df_tiktok['value'].min()) / (df_tiktok['value'].max() - df_tiktok['value'].min())
    
    # Get correlation coefficient pairing data.
    # Each element: (tiktok_spike_start, spotify_spike_start, coefficient)
    paired_correlations = get_correlation_coefficients(spotify_id, tiktok_id)
    
    # Also retrieve the full spike intervals (start, end) for both platforms.
    (spotify_spike_intervals, _), (tiktok_spike_intervals, _) = \
        find_spikes_in_normalized_series(spotify_id, tiktok_id)
    
    # Plot background normalized time series.
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_spotify['date'], df_spotify['normalized'], label='Spotify (Reach)', color='blue', alpha=0.7)
    ax.plot(df_tiktok['date'], df_tiktok['normalized'], label='TikTok', color='red', alpha=0.7)
    
    # Format x-axis for dates.
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    
    # Overlay spike markers (dashed for starts, ".-" for ends)
    # Plot spike start markers.
    for interval in spotify_spike_intervals:
        s_start, s_end = interval
        ax.axvline(s_start, color='blue', linestyle='--', alpha=0.8, label='Spotify Spike Start')
    for interval in tiktok_spike_intervals:
        t_start, t_end = interval
        ax.axvline(t_start, color='red', linestyle='--', alpha=0.8, label='TikTok Spike Start')
    
    # Plot spike end markers with ".-" style. We use ax.plot to simulate a vertical line with markers.
    y_limits = ax.get_ylim()
    for interval in spotify_spike_intervals:
        s_start, s_end = interval
        # Plot a vertical line from bottom to top with marker at the end.
        ax.plot([s_end, s_end], y_limits, "b-.", label='Spotify Spike End', alpha=0.8)
    for interval in tiktok_spike_intervals:
        t_start, t_end = interval
        ax.plot([t_end, t_end], y_limits, "r-.", label='TikTok Spike End', alpha=0.8)
    
    # Overlay correlation coefficient annotations.
    for t_start, s_start, coeff in paired_correlations:
        # Find midpoint between the paired spike starts.
        mid_point = t_start + (s_start - t_start) / 2
        ax.annotate(f"corr: {coeff:.2f}", xy=(mid_point, 0.65), xytext=(mid_point, 0.85),
                    arrowprops=dict(arrowstyle="->", color='black'),
                    ha='center', fontsize=10, color='black')
    
    # Remove duplicate legend entries.
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())
    
    ax.set_title(f"Correlation Coefficients for Paired Spikes for {song_name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized Value")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# --- Example usage ---
if __name__ == "__main__":
    spotify_id = 'njtwgzci'
    tiktok_id = 'njtwgzci'
    coeffs = get_correlation_coefficients(spotify_id, tiktok_id)
    print("Correlation Coefficients (tiktok_jump / spotify_jump) for the paired spikes:")
    for (t_start, s_start, c) in coeffs:
        print(f"TikTok Spike at {t_start} paired with Spotify Spike at {s_start}: Coefficient = {c:.2f}")
        
    plot_correlation_coefficients(spotify_id, tiktok_id)