import requests
import pandas as pd
import os

def get_spotify_playlist_series(song_id: str):
    csv_path = f"../../spotify_playlists_dataset/spotify_playlist_series_{song_id}.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        track_name = df['track_name'].iloc[0]
        last_90_data = df[['timestamp', 'value']].values.tolist()
        return track_name, last_90_data

    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data

def get_spotify_reach_series(song_id: str):
    csv_path = f"../../spotify_reach_dataset/spotify_reach_series_{song_id}.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        track_name = df['track_name'].iloc[0]
        last_90_data = df[['timestamp', 'value']].values.tolist()
        return track_name, last_90_data

    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][1]['data'][-90:]
        return track_name, last_90_data

def get_tiktok_series(song_id: str):
    csv_path = f"../../tiktok_series_dataset/tiktok_series_{song_id}.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        track_name = df['track_name'].iloc[0]
        last_90_data = df[['timestamp', 'value']].values.tolist()
        return track_name, last_90_data

    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=tiktok")
    if res.status_code != 200:
        return None
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data

def get_youtube_series(song_id: str): # video views
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=youtube")
    if res.status_code != 200:
        return None
    
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        artist_name = parsed_data['trackInfo']['artistName']
        avatar = parsed_data['trackInfo']['avatar']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data, artist_name, avatar

def get_shazam_series(song_id: str): # shazams
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=shazam")
    if res.status_code != 200:
        return None
    
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        artist_name = parsed_data['trackInfo']['artistName']
        avatar = parsed_data['trackInfo']['avatar']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data, artist_name, avatar
    
def get_soundcloud_series(song_id: str): # streams
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=soundcloud")
    if res.status_code != 200:
        return None
    
    parsed_data = res.json()
    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        artist_name = parsed_data['trackInfo']['artistName']
        avatar = parsed_data['trackInfo']['avatar']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data, artist_name, avatar
    
# print(get_spotify_reach_series(song_id='njtwgzci'))
print(get_soundcloud_series(song_id='njtwgzci'))
