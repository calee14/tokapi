#%%
from src.utils.song_graphs import find_spikes_in_normalized_series

spotify_id = 'njtwgzci'
tiktok_id = 'njtwgzci'

# Get spike intervals for Spotify and TikTok.
# Each interval is assumed to be a tuple (start_time, end_time) where start_time is a datetime object.
spotify_spike_intervals, tiktok_spike_intervals = find_spikes_in_normalized_series(spotify_id, tiktok_id)

# Extract only the start timestamps from each set of intervals
spotify_start_times = [interval[0] for interval in spotify_spike_intervals]
tiktok_start_times = [interval[0] for interval in tiktok_spike_intervals]

# Create a copy of Spotify start times to remove matched spikes
available_spotify_starts = spotify_start_times.copy()

# For each TikTok spike, find the nearest eligible Spotify spike start and calculate the delay (in days)
# Also, include an identifier for the paired spikes in a tuple: (tiktok_spike, spotify_spike, delay_days)
paired_spikes = []
for t_time in tiktok_start_times:
    nearest_spotify = None
    min_diff = None
    for s_time in available_spotify_starts:
        diff = abs((s_time - t_time).total_seconds())
        if min_diff is None or diff < min_diff:
            min_diff = diff
            nearest_spotify = s_time
    if nearest_spotify is not None:
        # Calculate delay in days (can be positive or negative)
        delay_days = (nearest_spotify - t_time).total_seconds() / 86400.0
        # Append a tuple with identifier details: (TikTok spike, Spotify spike, delay)
        paired_spikes.append((t_time, nearest_spotify, delay_days))
        # Remove the matched Spotify spike start so it can't be paired again
        available_spotify_starts.remove(nearest_spotify)

print("Paired spikes (TikTok spike, Spotify spike, time delay in days):")
for pair in paired_spikes:
    print(pair)