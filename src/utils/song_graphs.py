#%%
import os
import requests
import pandas as pd
import plotly.graph_objects as go

def get_spotify_playlist_series(song_id: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, f"../../spotify_playlists_dataset/spotify_playlist_series_{song_id}.csv")
    if os.path.exists(csv_path):
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            track_name = lines[0].strip()
            data = [(int(line.split(',')[0]), int(line.split(',')[1])) for line in lines[1:-2] if line.strip()]
            artist_name = lines[-2].strip()
            avatar = lines[-1].strip()
        return track_name, data, artist_name, avatar

    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:] if len(parsed_data['chart']['seriesData'][0]['data']) >= 90 else parsed_data['chart']['seriesData'][0]['data'][len(parsed_data['chart']['seriesData'][0]['data']):]
        artist_name = parsed_data['trackInfo']['artistName']
        avatar = parsed_data['trackInfo']['avatar']
        return track_name, last_90_data, artist_name, avatar

def get_spotify_reach_series(song_id: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, f"../../spotify_reach_dataset/spotify_reach_series_{song_id}.csv")
    if os.path.exists(csv_path):
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            track_name = lines[0].strip()
            data = [(int(line.split(',')[0]), int(line.split(',')[1])) for line in lines[1:-2] if line.strip()]
            artist_name = lines[-2].strip()
            avatar = lines[-1].strip()
        return track_name, data, artist_name, avatar

    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:] if len(parsed_data['chart']['seriesData'][0]['data']) >= 90 else parsed_data['chart']['seriesData'][0]['data'][len(parsed_data['chart']['seriesData'][0]['data']):]
        artist_name = parsed_data['trackInfo']['artistName']
        avatar = parsed_data['trackInfo']['avatar']
        return track_name, last_90_data, artist_name, avatar

def get_tiktok_series(song_id: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, f"../../tiktok_series_dataset/tiktok_series_{song_id}.csv")
    if os.path.exists(csv_path):
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            track_name = lines[0].strip()
            data = [(int(line.split(',')[0]), int(line.split(',')[1])) for line in lines[1:-2] if line.strip()]
            artist_name = lines[-2].strip()
            avatar = lines[-1].strip()
        return track_name, data, artist_name, avatar

    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=tiktok")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:] if len(parsed_data['chart']['seriesData'][0]['data']) >= 90 else parsed_data['chart']['seriesData'][0]['data'][len(parsed_data['chart']['seriesData'][0]['data']):]
        artist_name = parsed_data['trackInfo']['artistName']
        avatar = parsed_data['trackInfo']['avatar']
        return track_name, last_90_data, artist_name, avatar

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
        return None, None, None, None

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
        return [(x - min_val) / (max_val - min_val + pow(1, -8)) for x in lst] # check for division by 0
    spotify_normalized = pd.Series(min_max_normalize(spotify_series))
    tiktok_normalized = pd.Series(min_max_normalize(tiktok_series))

    # Find spikes
    (spotify_spike_dates, spotify_spike_values), (tiktok_spike_dates, tiktok_spike_values) = find_spikes_in_normalized_series(spotify_id, tiktok_id)
    
    # Determine causation
    causation = determine_causation(spotify_spike_dates, tiktok_spike_dates)
    
    # Create Plotly figure
    fig = go.Figure()

    # Add normalized series traces
    fig.add_trace(go.Scatter(
        x=spotify_dates,
        y=spotify_normalized,
        mode='lines',
        name='Spotify (normalized)',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=tiktok_dates,
        y=tiktok_normalized,
        mode='lines',
        name='TikTok (normalized)',
        line=dict(color='red')
    ))

    # Add markers for causation spikes and shade the causation areas
    for (start_spike, start_type, end_spike, end_type) in causation:
        if start_type == 'spotify' and end_type == 'tiktok':
            start_val = spotify_normalized.loc[spotify_dates == start_spike[0]].values[0]
            end_val = tiktok_normalized.loc[tiktok_dates == end_spike[1]].values[0]
            fig.add_shape(
                type="line",
                x0=start_spike[0],
                y0=0,
                x1=start_spike[0],
                y1=1,
                yref="paper",
                line=dict(color="blue", dash="dash")
            )
            fig.add_shape(
                type="line",
                x0=end_spike[1],
                y0=0,
                x1=end_spike[1],
                y1=1,
                yref="paper",
                line=dict(color="red", dash="dash")
            )
            fig.add_vrect(
                x0=start_spike[0],
                x1=end_spike[1],
                fillcolor="green",
                opacity=0.3,
                layer="below",
                line_width=0
            )
            # Add dots for start and end points
            fig.add_trace(go.Scatter(
                x=[start_spike[0], end_spike[1]],
                y=[start_val, end_val],
                mode='markers',
                marker=dict(color=['blue', 'red'], size=10),
                name='Critical Points'
            ))
            # Calculate the coefficient as the change in TikTok divided by the change in Spotify
            tiktok_change = end_val - tiktok_normalized.loc[tiktok_dates == end_spike[0]].values[0]
            spotify_change = spotify_normalized.loc[spotify_dates == start_spike[1]].values[0] - start_val
            if spotify_change != 0:
                coefficient = tiktok_change / spotify_change
                mid_point = start_spike[0] + (end_spike[1] - start_spike[0]) / 2
                delay = abs((end_spike[1] - start_spike[0]).days)
                fig.add_annotation(
                    x=mid_point,
                    y=0.5,
                    text=f"coeff: {coefficient:.2f}<br>delay: {delay:.2f} {'day' if abs(delay-1)<1e-6 else 'days'}",
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=-30,
                    font=dict(size=12, color="black", weight="bold")
                )
        elif start_type == 'tiktok' and end_type == 'spotify':
            start_val = tiktok_normalized.loc[tiktok_dates == start_spike[0]].values[0]
            end_val = spotify_normalized.loc[spotify_dates == end_spike[1]].values[0]
            fig.add_shape(
                type="line",
                x0=start_spike[0],
                y0=0,
                x1=start_spike[0],
                y1=1,
                yref="paper",
                line=dict(color="red", dash="dash")
            )
            fig.add_shape(
                type="line",
                x0=end_spike[1],
                y0=0,
                x1=end_spike[1],
                y1=1,
                yref="paper",
                line=dict(color="blue", dash="dash")
            )
            fig.add_vrect(
                x0=start_spike[0],
                x1=end_spike[1],
                fillcolor="green",
                opacity=0.3,
                layer="below",
                line_width=0
            )
            # Add dots for start and end points
            fig.add_trace(go.Scatter(
                x=[start_spike[0], end_spike[1]],
                y=[start_val, end_val],
                mode='markers',
                marker=dict(color=['red', 'blue'], size=10),
                name='Critical Points'
            ))
            # Calculate the coefficient as the change in Spotify divided by the change in TikTok
            spotify_change = end_val - spotify_normalized.loc[spotify_dates == end_spike[0]].values[0]
            tiktok_change = tiktok_normalized.loc[tiktok_dates == start_spike[1]].values[0] - start_val
            if tiktok_change != 0:
                coefficient = spotify_change / tiktok_change
                mid_point = start_spike[0] + (end_spike[1] - start_spike[0]) / 2
                delay = abs((end_spike[1] - start_spike[0]).days)
                fig.add_annotation(
                    x=mid_point,
                    y=0.5,
                    text=f"coeff: {coefficient:.2f}<br>delay: {delay:.2f} {'day' if abs(delay-1)<1e-6 else 'days'}",
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=-30,
                    font=dict(size=12, color="black", weight="bold")
                )

    fig.update_layout(
        title=f"Spotify and TikTok Series for {song_name}",
        xaxis_title='Date',
        yaxis_title='Normalized Value',
        legend_title='Series',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig, spotify_dates, spotify_normalized, tiktok_dates, tiktok_normalized

# Example usage:
if __name__ == "__main__":
    fig, spotify_dates, spotify_normalized, tiktok_dates, tiktok_normalized = plot_normalized_series_with_spikes(spotify_id='c7vi4fny', tiktok_id='c7vi4fny')
    fig.show()
# %%