import requests

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

def get_tidal_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=tidal")

    if res.status_code != 200:
        return None
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data
    
def get_shazam_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=shazam")

    if res.status_code != 200:
        return None
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data

def get_youtube_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=youtube")

    if res.status_code != 200:
        return None
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data

# print(get_spotify_playlist_series(song_id='njtwgzci'))
# print(get_spotify_reach_series(song_id='njtwgzci'))
# print(get_spotify_reach_series(song_id='njtwgzci'))
