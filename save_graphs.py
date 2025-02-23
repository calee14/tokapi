import requests
import csv
import pandas as pd
import matplotlib.pyplot as plt

def get_spotify_playlist_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")

    if res.status_code != 200:
        return None
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data

def get_spotify_reach_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")

    if res.status_code != 200:
        return None
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][1]['data'][-90:]
        return track_name, last_90_data
    
def get_tiktok_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=tiktok")

    if res.status_code != 200:
        return None
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data

def write_csv(filename: str, data, header=["Timestamp", "Value"]):
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for row in data:
            writer.writerow(row)

def plot_normalized_series(spotify_id: str, tiktok_id: str):
    spotify_data = get_spotify_playlist_series(spotify_id)[1]
    tiktok_data = get_tiktok_series(tiktok_id)

    if spotify_data is None or tiktok_data is None:
        print("Error fetching one or both data series.")
        return

    spotify_values = [entry[1] for entry in spotify_data]
    tiktok_values = [entry[1] for entry in tiktok_data]

    spotify_series = pd.Series(spotify_values)
    tiktok_series = pd.Series(tiktok_values)

    spotify_normalized = spotify_series / spotify_series.max()
    tiktok_normalized = tiktok_series / tiktok_series.max()

    plt.figure(figsize=(10, 5))
    plt.plot(spotify_normalized, label='Spotify (normalized)')
    plt.plot(tiktok_normalized, label='TikTok (normalized)')
    plt.xlabel('Index')
    plt.ylabel('Normalized Value')
    plt.title('Normalized Song Data from Spotify and TikTok')
    plt.legend()
    plt.show()

# if __name__ == "__main__":
#     spotify_data = get_spotify_playlist_series('njtwgzci')[1]
#     write_csv('test.csv', spotify_data)

'''
def main():
    with open("src/utils/songs", "r") as file:
        codes = file.read().splitlines()

    for code in codes:
        if code == '49gk6oeq':
            continue
        print(f"Processing song ID: {code}")
        series = get_spotify_reach_series(code)[1]
        if series is None:
            print(f"No data found for {code}.")
            continue
        if len(series) > 0:
            filename = f"spotify_reach_series_{code}.csv"
            write_csv(filename, series)
            print(f"Saved Spotify Reach data for {code} to {filename}")
        else:
            print(f"Not enough series available for song ID {code}.")

if __name__ == "__main__":
    main()
'''

