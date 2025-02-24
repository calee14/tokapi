import dash
from dash import html, dcc

dash.register_page(__name__, path='/results', name="Results", order=4)

layout = html.Div([
    html.H1("Results", style={'textAlign': 'center', 'marginTop': '40px'}),
    
    # Create an HTML table that supports LaTeX in one cell via dcc.Markdown.
    html.Div(
        html.Table([
            html.Thead(
                html.Tr([
                    html.Th(""),
                    html.Th("Spotify", style={'padding': '10px', 'border': '1px solid black'}),
                    html.Th("TikTok", style={'padding': '10px', 'border': '1px solid black'})
                ], style={'textAlign': 'center', 'fontSize': '20px'})
            ),
            html.Tbody([
                html.Tr([
                    html.Td("C", style={'padding': '10px', 'border': '1px solid black', 'fontSize': '20px', 'textAlign': 'center'}),
                    html.Td("1.53", style={'padding': '10px', 'border': '1px solid black', 'fontSize': '20px', 'textAlign': 'center'}),
                    html.Td("2.08", style={'padding': '10px', 'border': '1px solid black', 'fontSize': '20px', 'textAlign': 'center'})
                ]),
                html.Tr([
                    html.Td(dcc.Markdown("$t_d$", mathjax=True), style={'padding': '10px', 'border': '1px solid black', 'fontSize': '20px', 'textAlign': 'center'}),
                    html.Td("7.55", style={'padding': '10px', 'border': '1px solid black', 'fontSize': '20px', 'textAlign': 'center'}),
                    html.Td("9.21", style={'padding': '10px', 'border': '1px solid black', 'fontSize': '20px', 'textAlign': 'center'})
                ])
            ])
        ], style={'width': '70%', 'margin': '0 auto', 'borderCollapse': 'collapse'}),
        style={'marginBottom': '0px'}
    ),
    
    # Explanation text with reduced top margin
    html.Div([
        html.P("Since the TikTok 1st coefficient > the Spotify 1st coefficient,"),
        html.P("this tells us that TikTok may have a bigger influence on Spotify than vice versa."),
        html.Br(),
        html.P("Since the TikTok 1st time delay > the Spotify 1st time delay,"),
        html.P("this tells us that TikTok may have a smaller influence on Spotify than vice versa."),
        html.Br(),
        html.P("We cannot confidently conclude that TikTok is a music trend setter in the past 90 days.")
    ], style={'fontSize': '20px', 'textAlign': 'center', 'marginTop': '10px', 'paddingTop': '0px'})
], style={'margin': '10px'})