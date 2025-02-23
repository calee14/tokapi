#%%
import requests
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf

def get_spotify_reach_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][1]['data'][-90:]
        return track_name, last_90_data

data = pd.read_csv('spotify_reach_dataset/spotify_reach_series_yuntz7bp.csv')
song_name = get_spotify_reach_series('yuntz7bp')[0]


if 'Value' in data.columns:
    series = data['Value']
else:
    raise KeyError("Column 'reach' not found. Please check your CSV file for the correct column name.")

plot_acf(series, lags=80, alpha=0.05)
plt.title("ACF Plot for Spotify Reach Series")
plt.xlabel("Lag")
plt.ylabel("Autocorrelation")
plt.title(f"Spotify and TikTok Series for {song_name}")
plt.show()

plot_pacf(series, lags=20, alpha=0.05)
plt.title("Partial Autocorrelation Function (PACF) Plot for Spotify Reach Series")
plt.xlabel("Lag")
plt.ylabel("Partial Autocorrelation")
plt.show()

# %%


def get_tiktok_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=tiktok")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        print("last_90_data", last_90_data)
        return track_name, last_90_data

data = pd.read_csv('tiktok_series_dataset/tiktok_series_yuntz7bp.csv')
song_name = get_tiktok_series('yuntz7bp')[0]


if 'Value' in data.columns:
    series = data['Value']
else:
    raise KeyError("Column 'reach' not found. Please check your CSV file for the correct column name.")

plot_acf(series, lags=80, alpha=0.05)
plt.title("ACF Plot for Spotify Reach Series")
plt.xlabel("Lag")
plt.ylabel("Autocorrelation")
plt.title(f"Spotify and TikTok Series for {song_name}")
plt.show()

plot_pacf(series, lags=20, alpha=0.05)
plt.title("Partial Autocorrelation Function (PACF) Plot for Spotify Reach Series")
plt.xlabel("Lag")
plt.ylabel("Partial Autocorrelation")
plt.show()