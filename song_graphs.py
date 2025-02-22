#%%
import requests
import pandas as pd
import matplotlib.pyplot as plt

def get_spotify_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        return parsed_data['chart']['seriesData'][0]['data']

def get_tiktok_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=tiktok")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        return parsed_data['chart']['seriesData'][0]['data']

def plot_normalized_series(spotify_id: str, tiktok_id: str):
    # Retrieve series data
    spotify_data = get_spotify_series(spotify_id)
    tiktok_data = get_tiktok_series(tiktok_id)

    if spotify_data is None or tiktok_data is None:
        print("Error fetching one or both data series.")
        return

    # Extract numeric values (assuming they are the second element in each sublist)
    spotify_values = [entry[1] for entry in spotify_data]
    tiktok_values = [entry[1] for entry in tiktok_data]

    # Convert lists to pandas Series and normalize
    spotify_series = pd.Series(spotify_values)
    tiktok_series = pd.Series(tiktok_values)

    # Normalize by dividing by the maximum value in each series
    spotify_normalized = spotify_series / spotify_series.max()
    tiktok_normalized = tiktok_series / tiktok_series.max()

    # Plotting both normalized series
    plt.figure(figsize=(10, 5))
    plt.plot(spotify_normalized, label='Spotify (normalized)')
    plt.plot(tiktok_normalized, label='TikTok (normalized)')
    plt.xlabel('Index')
    plt.ylabel('Normalized Value')
    plt.title('Normalized Song Data from Spotify and TikTok')
    plt.legend()
    plt.show()

print(get_spotify_series(song_id='njtwgzci'))

# Example usage:
if __name__ == "__main__":
    plot_normalized_series(spotify_id='njtwgzci', tiktok_id='njtwgzci')