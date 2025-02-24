#%%
from utils.song_graphs import (
    get_spotify_reach_series,
    get_tiktok_series,
    find_spikes_in_normalized_series,
    determine_causation
)
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

def generate_time_delay_graph(spotify_id, tiktok_id):
    # Retrieve series data
    spotify_data = get_spotify_reach_series(spotify_id)[1]
    song_name = get_spotify_reach_series(spotify_id)[0]
    tiktok_data = get_tiktok_series(tiktok_id)[1]

    if spotify_data is None or tiktok_data is None:
        print("Error fetching one or both data series.")
        return None

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

    causation = determine_causation(spotify_spike_dates, tiktok_spike_dates)

    paired_spikes = []
    for (start_spike, start_type, end_spike, end_type) in causation:
        if start_type == 'spotify' and end_type == 'tiktok':
            start_val = spotify_normalized.loc[spotify_dates == start_spike[0]].values[0]
            end_val = tiktok_normalized.loc[tiktok_dates == end_spike[0]].values[0]
            paired_spikes.append((start_spike[0], end_spike[0], abs(end_spike[0] - start_spike[0]).days))
        elif start_type == 'tiktok' and end_type == 'spotify':
            start_val = tiktok_normalized.loc[tiktok_dates == start_spike[0]].values[0]
            end_val = spotify_normalized.loc[spotify_dates == end_spike[0]].values[0]
            paired_spikes.append((end_spike[0], start_spike[0], abs(start_spike[0] - end_spike[0]).days))

    # Create Plotly figure
    fig = go.Figure()

    # Plot the background normalized time series for Spotify and TikTok
    fig.add_trace(go.Scatter(
        x=spotify_dates,
        y=spotify_normalized,
        mode='lines',
        name='Spotify (Reach)',
        line=dict(color='blue'),
        opacity=0.7
    ))
    fig.add_trace(go.Scatter(
        x=tiktok_dates,
        y=tiktok_normalized,
        mode='lines',
        name='TikTok',
        line=dict(color='red'),
        opacity=0.7
    ))

    # Plot vertical lines (spike markers) and annotate the absolute delay for each paired spike.
    for s_time, t_time, delay in paired_spikes:
        # Calculate midpoint between s_time and t_time for annotation
        mid_point = s_time + (t_time - s_time) / 2
        # Annotate the absolute delay value
        fig.add_annotation(
            x=mid_point,
            y=0.5,
            text=f"{delay:.2f} days",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-30,
            font=dict(size=12, color="black", weight="bold")
        )
        # Add vertical lines and markers for start and end points
        fig.add_shape(
            type="line",
            x0=s_time,
            y0=0,
            x1=s_time,
            y1=1,
            yref="paper",
            line=dict(color="blue", dash="dot")
        )
        fig.add_shape(
            type="line",
            x0=t_time,
            y0=0,
            x1=t_time,
            y1=1,
            yref="paper",
            line=dict(color="red", dash="dash")
        )
        fig.add_trace(go.Scatter(
            x=[s_time, t_time],
            y=[spotify_normalized.loc[spotify_dates == s_time].values[0], tiktok_normalized.loc[tiktok_dates == t_time].values[0]],
            mode='markers',
            marker=dict(color=['blue', 'red'], size=10),
            name='Critical Points'
        ))

    fig.update_layout(
        title=f"Absolute Time Delay Between Paired Spikes for {song_name}",
        xaxis_title='Date',
        yaxis_title='Normalized Value',
        legend_title='Series',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig, spotify_dates, spotify_normalized, tiktok_dates, tiktok_normalized

# Example usage:
if __name__ == "__main__":
    fig, spotify_dates, spotify_normalized, tiktok_dates, tiktok_normalized = generate_time_delay_graph(spotify_id='c7vi4fny', tiktok_id='c7vi4fny')
    fig.show()