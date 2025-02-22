import requests

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

# print(get_spotify_series(song_id='njtwgzci'))
print(get_tiktok_series(song_id='n5i60mse'))
