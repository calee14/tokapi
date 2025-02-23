import dash
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from utils.song_stats import (
    get_spotify_playlist_series,
    get_spotify_reach_series,
    get_tiktok_series
)

dash.register_page(__name__, path='/', name="About")

# Get data from song_stats.py functions using a sample song_id
spotify_playlist_result = get_spotify_playlist_series(song_id='njtwgzci')
spotify_reach_result = get_spotify_reach_series(song_id='njtwgzci')
tiktok_result = get_tiktok_series(song_id='njtwgzci')

# Create dataframes from the returned series (assumes structure: [timestamp, value])
df_spotify_playlist = pd.DataFrame(spotify_playlist_result[1], columns=['timestamp', 'value'])
df_spotify_playlist['date'] = pd.to_datetime(df_spotify_playlist['timestamp'], unit='ms')

df_spotify_reach = pd.DataFrame(spotify_reach_result[1], columns=['timestamp', 'value'])
df_spotify_reach['date'] = pd.to_datetime(df_spotify_reach['timestamp'], unit='ms')

df_tiktok = pd.DataFrame(tiktok_result[1], columns=['timestamp', 'value'])
df_tiktok['date'] = pd.to_datetime(df_tiktok['timestamp'], unit='ms')

# Normalize the y-values for each series
df_spotify_playlist['normalized'] = df_spotify_playlist['value'] / df_spotify_playlist['value'].max()
df_spotify_reach['normalized'] = df_spotify_reach['value'] / df_spotify_reach['value'].max()
df_tiktok['normalized'] = df_tiktok['value'] / df_tiktok['value'].max()

# Create a combined Plotly figure with all series in one graph (using a line graph)
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_spotify_playlist['date'],
    y=df_spotify_playlist['normalized'],
    mode='lines',
    name=f"{spotify_playlist_result[0]} - Spotify Playlist",
    line=dict(color='blue')
))

fig.add_trace(go.Scatter(
    x=df_spotify_reach['date'],
    y=df_spotify_reach['normalized'],
    mode='lines',
    name=f"{spotify_reach_result[0]} - Spotify Reach",
    line=dict(color='green')
))

fig.add_trace(go.Scatter(
    x=df_tiktok['date'],
    y=df_tiktok['normalized'],
    mode='lines',
    name=f"{tiktok_result[0]} - TikTok",
    line=dict(color='red')
))

# Define axis style with larger fonts for labels and ticks
axis_style = dict(
    title_font=dict(size=22, color='black', family='Merriweather Sans'),
    tickfont=dict(size=18, color='black', family='Merriweather Sans'),
    showgrid=False,
    ticks='outside',
    ticklen=5,
    tickwidth=2,
    tickcolor='black'
)

# Update layout for the combined figure; remove built-in legend and add axis lines
artist_name = spotify_playlist_result[0]  # assuming the artist's or track's name is here
fig.update_layout(
    showlegend=False,  # Remove built-in legend from the figure
    xaxis=dict(
        title='Date',
        showline=True,
        linecolor='black',
        linewidth=2,
        **axis_style
    ),
    yaxis=dict(
        title='Normalized Value',
        showline=True,
        linecolor='black',
        linewidth=2,
        **axis_style
    ),
    title=dict(text=f"Song Statistics for {artist_name}", font=dict(size=28, color='black', family='Merriweather Sans')),
    plot_bgcolor='white',
    paper_bgcolor='white',
    width=700,   # Increased width for a larger graph
    height=700   # Increased height to keep the graph square
)

# Create a custom external legend
external_legend = html.Div([
    html.Span([
        html.Span(style={'backgroundColor': 'blue', 'display': 'inline-block',
                           'width': '12px', 'height': '12px', 'marginRight': '5px'}),
        html.Span(f"{spotify_playlist_result[0]} - Spotify Playlist", style={'marginRight': '20px'})
    ], style={'display': 'inline-block', 'marginRight': '20px'}),
    html.Span([
        html.Span(style={'backgroundColor': 'green', 'display': 'inline-block',
                           'width': '12px', 'height': '12px', 'marginRight': '5px'}),
        html.Span(f"{spotify_reach_result[0]} - Spotify Reach", style={'marginRight': '20px'})
    ], style={'display': 'inline-block', 'marginRight': '20px'}),
    html.Span([
        html.Span(style={'backgroundColor': 'red', 'display': 'inline-block',
                           'width': '12px', 'height': '12px', 'marginRight': '5px'}),
        html.Span(f"{tiktok_result[0]} - TikTok")
    ], style={'display': 'inline-block'})
], style={'textAlign': 'center', 'marginBottom': '20px'})

# Center the graph within the page
graph_container = html.Div(
    dcc.Graph(figure=fig),
    style={'display': 'flex', 'justifyContent': 'center'}
)

layout = html.Div([
    html.H1("Song Statistics", style={'color': 'black', 'textAlign': 'center'}),
    external_legend,
    graph_container
], style={'margin': '20px'})