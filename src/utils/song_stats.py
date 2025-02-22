import requests

def get_spotify_series(artist_id: str, song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{artist_id}/top?idUnique={song_id}&source=spotify")

    if res.status_code != 200:
        return 
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        return parsed_data['chart']['seriesData'][0]['data']

def get_tiktok_series(artist_id: str, song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{artist_id}/top?idUnique={song_id}&source=tiktok")

    if res.status_code != 200:
        return 
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        return parsed_data['chart']['seriesData'][0]['data']

# print(get_spotify_series(artist_id='njtwgzci', song_id='kflctw05'))
# print(get_tiktok_series(artist_id='njtwgzci', song_id='kflctw05'))
