import dash
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go
import pandas as pd
from utils.song_graphs import (
    get_spotify_reach_series,
    get_tiktok_series,
    plot_normalized_series_with_spikes
)
from utils.time_delay import generate_time_delay_graph

dash.register_page(__name__, path='/', name="About")

# Dictionary of {song_name: song_code}
song_dict = {'Not Like Us': 'c7vi4fny','Runaway': 'o6czgimx', 'She Will': 'n5i60mse', 'LOVE. FEAT. ZACARI.': 'a5ztdk8h', 'Dramamine': 'mtzqw83r', 'Glue Song': 'bjux4okf', 'BIRDS OF A FEATHER': 'qm8rn2e4', 'WILDFLOWER': '7ljt0hoe', 'Soft Spot': '14wfukzh', 'Dumb Crasy': 'e0sgixcm', 'Die With A Smile': '1nz06lk3', 'APT.': 'fc8qjl3m', 'That’s So True': 'fb32ov0h', 'blue': 'x85of12m', 'Heavy': 'njtwgzci', 'Like Him (feat. Lola Young)': '4uo2i0yw', 'anything': 'h3sblgqy', 'Faneto': '49gk6oeq', 'Oblivion': 'o92qv3ys', 'DENIAL IS A RIVER': '50rq9nmp', 'Gas Pedal': 'bplr6hso', 'Headlock': '2rg1axdf', 'Abracadabra': '1rb8pz6f', 'you not the same': 'wgd4bvl1', 'No One Noticed (Extended Spanish)': 'tk3w0e74', 'Loco': '1rd5i93x', 'Chest Pain (I Love)': 'emhkbl4c', 'KHÔNG SAO CẢ (feat. 7dnight)': 'ufvjdt73', 'All The Stars (with SZA)': '1qaf6tbw', 'Bad At Love': 'h7v3unlb', 'luther (with sza)': 'a290fxbt', 'peekaboo (feat. azchike)': '5jk2ct1d', '30 For 30 (with Kendrick Lamar)': '7rat3fw1', 'Tweaker': '49fhq386', 'QKThr': '0ectual7', "Big Girls Don't Cry (Personal)": 'h7b5gt1l', 'Shake Dat Ass (Twerk Song)': '3o8bcqis', "Let's Groove": '89rho01p', 'Oh My Angel': 'rfavoyeh', 'Champagne Coast': '2lmeytah', 'Again': 'utsgjrif', 'Azul': 'izgr20qb', 'Sweet Heat Lightning': 'evq3bruf', 'tv off (feat. lefty gunplay)': 'nv4xpgkm', 'You Love Me': 'yuntz7bp', 'White Ferrari': 'vyz39mwr', 'Paper Planes': '30xu5rms', '7/11': 'g2l4db6q', 'come': '1hsuk5ag'}

# Dropdown menu options
dropdown_options = [{"label": song_name, "value": song_code} for song_name, song_code in song_dict.items()]

# Layout with dropdown menu
layout = html.Div([
    html.H1("Song Statistics", style={
        'color': 'black',
        'textAlign': 'center',
        'marginBottom': '20px'
    }),
    dcc.Dropdown(
        id='song-dropdown',
        options=dropdown_options,
        value=list(song_dict.values())[0],  # Default value
        style={'width': '50%', 'margin': '0 auto'}
    ),
    html.Div(id='graphs-container'),
    dcc.Store(id="playing-store", data=False),  # dcc.Store for play state
    html.Div(id='animate-dummy', style={'display': 'none'})  # dummy Div for animation callback
], style={'margin': '20px', 'paddingBottom': '100px'})

@callback(
    Output('graphs-container', 'children'),
    Input('song-dropdown', 'value')
)
def update_graphs(song_code):
    # Get data from song_stats.py functions using the selected song_code
    spotify_reach_result = get_spotify_reach_series(song_id=song_code)
    tiktok_result = get_tiktok_series(song_id=song_code)

    # Create dataframes from the returned series (assumes structure: [timestamp, value])
    df_spotify_reach = pd.DataFrame(spotify_reach_result[1], columns=['timestamp', 'value'])
    df_spotify_reach['date'] = pd.to_datetime(df_spotify_reach['timestamp'], unit='ms')

    df_tiktok = pd.DataFrame(tiktok_result[1], columns=['timestamp', 'value'])
    df_tiktok['date'] = pd.to_datetime(df_tiktok['timestamp'], unit='ms')

    # Normalize the y-values for each series
    df_spotify_reach['normalized'] = df_spotify_reach['value'] / df_spotify_reach['value'].max()
    df_tiktok['normalized'] = df_tiktok['value'] / df_tiktok['value'].max()

    track_name = tiktok_result[0]
    artist_name = tiktok_result[2]
    avatar = tiktok_result[3]

    # Create a combined Plotly figure with all series in one graph (using a line graph)
    fig, spotify_dates, spotify_normalized, tiktok_dates, tiktok_normalized = plot_normalized_series_with_spikes(song_code, song_code)
    fig_time_delay, spotify_dates_time_delay, spotify_normalized_time_delay, tiktok_dates_time_delay, tiktok_normalized_time_delay = generate_time_delay_graph(spotify_id=song_code, tiktok_id=song_code)

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
            **axis_style,
            range=[0,1]
        ),
        title=dict(
            text=f"Song Statistics for {track_name} - {artist_name}",
            font=dict(size=20, color='black', family='Merriweather Sans'),
            x=0.5  # center the title
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=800,
        height=600
    )

    fig_time_delay.update_layout(
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
            **axis_style,
            range=[0,1]
        ),
        title=dict(
            text=f"Time Delay Analysis for {track_name} - {artist_name}",
            font=dict(size=20, color='black', family='Merriweather Sans'),
            x=0.5  # center the title
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=800,
        height=600
    )

    # Create a custom external legend (optional)
    external_legend = html.Div([
        html.Span([
            html.Span(style={'backgroundColor': 'blue',
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

    # Center the graphs in their own containers
    graph_container = html.Div(
        dcc.Graph(id='graph', figure=fig),
        style={
            'width': '700px',
            'margin': '0 auto',
            'display': 'flex',
            'justifyContent': 'center'
        }
    )

    graph_time_delay_container = html.Div(
        dcc.Graph(id='graph-time-delay', figure=fig_time_delay),
        style={
            'width': '700px',
            'margin': '0 auto',
            'display': 'flex',
            'justifyContent': 'center'
        }
    )

    # Place the legend below the graphs (centered too)
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
            ".. line = the beginning of the spike, and -- line = the end of the spike.",
            style={'fontSize': '14px', 'textAlign': 'center', 'margin': '10px 0', 'fontStyle': 'italic'}
        )
    ])
    
    # Build animation frames (with fixed y-axis range [0,1])
    N = len(spotify_dates)
    frames = []

    # Frame 0: start with empty data.
    frames.append(go.Frame(
        data=[
            go.Scatter(x=[], y=[], mode='lines', line=dict(color='blue')),
            go.Scatter(x=[], y=[], mode='lines', line=dict(color='red'))
        ],
        layout=dict(
            xaxis=dict(visible=True),
            yaxis=dict(visible=True, range=[0,1])
        ),
        name='frame0'
    ))

    # Frames 1..N: gradually add data points for both traces.
    for i in range(1, N+1):
        frames.append(go.Frame(
            data=[
                go.Scatter(
                    x=spotify_dates[:i],
                    y=spotify_normalized[:i],
                    mode='lines',
                    line=dict(color='blue')
                ),
                go.Scatter(
                    x=tiktok_dates[:i],
                    y=tiktok_normalized[:i],
                    mode='lines',
                    line=dict(color='red')
                )
            ],
            name=f'frame{i}'
        ))

    fig.frames = frames
    fig_time_delay.frames = frames

    # Remove update menu from figure; animation will now be triggered via the play button.

    # Clientside callback to trigger animation when the play state (via playing-store) becomes True.
    dash.clientside_callback(
        """
        function(playing) {
            if (playing) {
                // Locate the actual Plotly plot within the dcc.Graph container.
                var graphDiv = document.getElementById('graph').getElementsByClassName('js-plotly-plot')[0];
                var graphTimeDelayDiv = document.getElementById('graph-time-delay').getElementsByClassName('js-plotly-plot')[0];
                if(graphDiv && graphTimeDelayDiv){
                    Plotly.animate(graphDiv, null, {
                        frame: {duration: 50, redraw: true},
                        transition: {duration: 500, easing: 'cubic-in-out'}
                    });
                    Plotly.animate(graphTimeDelayDiv, null, {
                        frame: {duration: 50, redraw: true},
                        transition: {duration: 500, easing: 'cubic-in-out'}
                    });
                }
            }
            return "";
        }
        """,
        Output('animate-dummy', 'children'),
        Input('playing-store', 'data')
    )
    # Add a dcc.Store for tracking play state
    store = dcc.Store(id="playing-store", data=False)
    animate_dummy = html.Div(id='animate-dummy', style={'display': 'none'})
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
    # Centered playback controls
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
            'width': '50px',
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


    return html.Div([
        graph_container,
        graph_time_delay_container,
        legend_container,
        description,
        bottom_bar,
        store,
        animate_dummy
    ])

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

# Clientside callback to trigger animation when the play state (via playing-store) becomes True.
dash.clientside_callback(
    """
    function(playing) {
        if (playing) {
            // Locate the actual Plotly plot within the dcc.Graph container.
            var graphDiv = document.getElementById('graph').getElementsByClassName('js-plotly-plot')[0];
            var graphTimeDelayDiv = document.getElementById('graph-time-delay').getElementsByClassName('js-plotly-plot')[0];
            if(graphDiv && graphTimeDelayDiv){
                Plotly.animate(graphDiv, null, {
                    frame: {duration: 50, redraw: true},
                    transition: {duration: 500, easing: 'cubic-in-out'}
                });
                Plotly.animate(graphTimeDelayDiv, null, {
                    frame: {duration: 50, redraw: true},
                    transition: {duration: 500, easing: 'cubic-in-out'}
                });
            }
        }
        return "";
    }
    """,
    Output('animate-dummy', 'children'),
    Input('playing-store', 'data')
)