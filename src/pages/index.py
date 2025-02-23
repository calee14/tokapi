import dash
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from utils.song_stats import (
    get_spotify_playlist_series,
    get_spotify_reach_series,
    get_tiktok_series
)
from utils.correlation import get_correlation_coefficients

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
    x=df_spotify_reach['date'],
    y=df_spotify_reach['normalized'],
    mode='lines',
    name=f"{spotify_reach_result[0]} - Spotify Playlist Reach",
    line=dict(color='green')
))

fig.add_trace(go.Scatter(
    x=df_tiktok['date'],
    y=df_tiktok['normalized'],
    mode='lines',
    name=f"{tiktok_result[0]} - TikTok Cumulative Video",
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

track_name = spotify_playlist_result[0]
artist_name = spotify_playlist_result[2]
avatar = spotify_playlist_result[3]

fig.update_layout(
    showlegend=False,
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
    title=dict(
        text=f"Song Statistics for {track_name} - {artist_name}",
        font=dict(size=28, color='black', family='Merriweather Sans'),
        x=0.5  # center the title
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    width=600,
    height=600
)

# Get paired spike data with correlation coefficients; each element is now:
# (tiktok_start, tiktok_end, spotify_start, spotify_end, coefficient)
paired_spikes = get_correlation_coefficients(spotify_id='njtwgzci', tiktok_id='njtwgzci')

for t_start, t_end, s_start, s_end, corr in paired_spikes:
    # Compute absolute delay using the spike start times
    delay = abs((s_start - t_start).total_seconds()) / 86400.0
    # Determine midpoints for annotation
    mid_start = t_start + (s_start - t_start) / 2
    mid_end = t_end + (s_end - t_end) / 2

    # Add vertical lines for spike starts (dashed lines)
    fig.add_shape(
        type="line",
        x0=t_start,
        y0=0,
        x1=t_start,
        y1=1,
        yref="paper",
        line=dict(color="red", dash="dash")
    )
    fig.add_shape(
        type="line",
        x0=s_start,
        y0=0,
        x1=s_start,
        y1=1,
        yref="paper",
        line=dict(color="green", dash="dash")
    )

    # Add vertical lines for spike ends (dash-dot lines)
    fig.add_shape(
        type="line",
        x0=t_end,
        y0=0,
        x1=t_end,
        y1=1,
        yref="paper",
        line=dict(color="red", dash="dashdot")
    )
    fig.add_shape(
        type="line",
        x0=s_end,
        y0=0,
        x1=s_end,
        y1=1,
        yref="paper",
        line=dict(color="green", dash="dashdot")
    )

    # Shade the area between each spike's start and end for TikTok and Spotify
    fig.add_vrect(
        x0=t_start,
        x1=t_end,
        fillcolor="red",
        opacity=0.2,
        layer="below",
        line_width=0
    )
    fig.add_vrect(
        x0=s_start,
        x1=s_end,
        fillcolor="green",
        opacity=0.2,
        layer="below",
        line_width=0
    )

    # Update the annotation text to use "day" if delay equals 1, otherwise "days"
    fig.add_annotation(
        x=mid_start,
        y=0.95,
        xref="x",
        yref="paper",
        text=f"corr: {corr:.2f}<br>delay: {delay:.2f} {'day' if abs(delay-1)<1e-6 else 'days'}",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-30,
        font=dict(size=12, color="black")
    )

# ... existing code above remains unchanged ...

# Create a custom external legend (optional)
external_legend = html.Div([
    html.Span([
        html.Span(style={'backgroundColor': 'green',
                           'display': 'inline-block',
                           'width': '12px', 'height': '12px', 'marginRight': '5px'}),
        html.Span(f"Spotify Playlist Reach", style={'marginRight': '20px'})
    ], style={'display': 'inline-block', 'marginRight': '20px'}),
    html.Span([
        html.Span(style={'backgroundColor': 'red',
                           'display': 'inline-block',
                           'width': '12px', 'height': '12px', 'marginRight': '5px'}),
        html.Span(f"TikTok")
    ], style={'display': 'inline-block'})
], style={'textAlign': 'center', 'marginBottom': '20px'})

# Center the graph in its own container
graph_container = html.Div(
    dcc.Graph(figure=fig),
    style={
        'width': '700px',
        'margin': '0 auto',
        'display': 'flex',
        'justifyContent': 'center'
    }
)

# Place the legend below the graph (centered too)
legend_container = html.Div(
    external_legend,
    style={'width': '700px', 'margin': '20px auto 0', 'textAlign': 'center'}
)

description = html.Div([
    html.P(
        f"Playlist Reach: The combined follower number of all Spotify playlists with 200+ followers {track_name} is currently on.",
        style={'fontSize': '16px', 'textAlign': 'center', 'margin': '10px 0'}
    ),
    html.P(
        f"Videos: The total number of videos containing {track_name}.",
        style={'fontSize': '16px', 'textAlign': 'center', 'margin': '10px 0'}
    ),
    html.P(
        "-- line = the beginning of the spike, and .- line = the end of the spike.",
        style={'fontSize': '14px', 'textAlign': 'center', 'margin': '10px 0', 'fontStyle': 'italic'}
    )
])

# Add a dcc.Store for tracking play state
store = dcc.Store(id="playing-store", data=False)

# Create a bottom bar similar to Spotify’s player bar with back, play/pause, and forward buttons and a non-clickable avatar.
bottom_bar = html.Div([
    # Avatar at the left corner
    html.Div(
        html.Img(src=avatar, id="avatar-img", style={
            'width': '50px',
            'height': '50px',
            'borderRadius': '50%',
            'objectFit': 'cover'
        }),
        style={'position': 'absolute', 'left': '20px', 'top': '50%', 'transform': 'translateY(-50%)'}
    ),
    # Playback controls centered in the bar
    html.Div([
        html.Button("⏮", id="back-btn", style={
            'fontSize': '30px',
            'background': 'none',
            'border': 'none',
            'color': 'white',
            'width': '50px',
            'height': '50px'
        }),
        html.Button("▶", id="playpause-btn", style={
            'fontSize': '30px',
            'background': 'none',
            'border': 'none',
            'color': 'white',
            'width': '50px',      # fixed size so layout doesn't shift
            'height': '50px',
            'margin': '0 20px'
        }),
        html.Button("⏭", id="forward-btn", style={
            'fontSize': '30px',
            'background': 'none',
            'border': 'none',
            'color': 'white',
            'width': '50px',
            'height': '50px'
        })
    ], style={'margin': '0 auto', 'display': 'flex', 'alignItems': 'center'})
], style={
    'position': 'fixed',
    'bottom': '0',
    'left': '0',
    'width': '100%',
    'height': '70px',
    'backgroundColor': '#121212',
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center',
    'zIndex': '1000',
    'padding': '0 20px'
})

layout = html.Div([
    html.H1("Song Statistics", style={
        'color': 'black',
        'textAlign': 'center',
        'marginBottom': '20px'
    }),
    graph_container,
    legend_container,
    description,
    bottom_bar,
    store
], style={'margin': '20px'})

# Callback to toggle play/pause state and update the play/pause button icon.
@callback(
    [Output("playing-store", "data"),
     Output("playpause-btn", "children")],
    [Input("playpause-btn", "n_clicks")],
    [State("playing-store", "data")],
    prevent_initial_call=True
)
def toggle_play(n_clicks, playing):
    if playing:
        return False, "▶"
    return True, "⏸"

# Callback to update the avatar styling to animate a slow spin when playing.
@callback(
    Output("avatar-img", "style"),
    [Input("playing-store", "data")]
)
def update_avatar(playing):
    base_style = {
        'width': '50px',
        'height': '50px',
        'borderRadius': '50%',
        'objectFit': 'cover',
        'marginLeft': '20px'
    }
    if playing:
        base_style["animation"] = "spin 4s linear infinite"
    else:
        base_style["animation"] = "none"
    return base_style