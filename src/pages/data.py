import dash
from dash import html, dcc

dash.register_page(__name__, path='/data', name="Data", order=3)

layout = html.Div([
    html.H1("Data", style={'textAlign': 'center', 'marginTop': '80px'}),
    dcc.Markdown(
        """
        Using popularity data of songs that are on the TikTok Billboard Top 50 from [Songstats](https://www.songstats.com), we analyzed time delay and correlation coefficients, $C$ and $t_d$.
        """,
        mathjax=True,
        style={'fontSize': '20px', 'textAlign': 'center', 'margin': '20px'}
    )
], style={'margin': '20px'})