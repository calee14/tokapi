import requests
import csv
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

def get_spotify_playlist_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")

    if res.status_code != 200:
        return None
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        artist_name = parsed_data['trackInfo']['artistName']
        avatar = parsed_data['trackInfo']['avatar']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data, artist_name, avatar

def get_spotify_reach_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=spotify")

    if res.status_code != 200:
        return None
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        artist_name = parsed_data['trackInfo']['artistName']
        avatar = parsed_data['trackInfo']['avatar']
        last_90_data = parsed_data['chart']['seriesData'][1]['data'][-90:]
        return track_name, last_90_data, artist_name, avatar
    
def get_tiktok_series(song_id: str):
    res = requests.get(f"https://data.songstats.com/api/v1/analytics_track/{song_id}/top?source=tiktok")

    if res.status_code != 200:
        return None
    
    parsed_data = res.json()

    if parsed_data['result'] == 'success':
        track_name = parsed_data['trackInfo']['trackName']
        artist_name = parsed_data['trackInfo']['artistName']
        avatar = parsed_data['trackInfo']['avatar']
        last_90_data = parsed_data['chart']['seriesData'][0]['data'][-90:]
        return track_name, last_90_data, artist_name, avatar

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
        name = get_spotify_reach_series(code)[0]
        artist = get_spotify_reach_series(code)[2]
        avatar = get_spotify_reach_series(code)[3]
        if series is None:
            print(f"No data found for {code}.")
            continue
        if len(series) > 0:
            filename = f"spotify_reach_series_{code}.csv"
          # write_csv(filename, series)
            with open(filename, "w", newline="") as file:
                file.write(name + "\n")
                writer = csv.writer(file)
                writer.writerows(series)
                file.write(artist + "\n")
                file.write(avatar)
            print(f"Saved Spotify Reach data for {code} to {filename}")
        else:
            print(f"Not enough series available for song ID {code}.")

if __name__ == "__main__":
    main()
'''

# print(get_spotify_reach_series('n5i60mse'))

'''
def main():
    with open("src/utils/songs", "r") as file:
        codes = file.read().splitlines()

    for code in codes:
        if code == '49gk6oeq':
            continue
        print(f"Processing song ID: {code}")
        series = get_spotify_playlist_series(code)[1]
        name = get_spotify_playlist_series(code)[0]
        artist = get_spotify_playlist_series(code)[2]
        avatar = get_spotify_playlist_series(code)[3]
        if series is None:
            print(f"No data found for {code}.")
            continue
        if len(series) > 0:
            filename = f"spotify_playlist_series_{code}.csv"
          # write_csv(filename, series)
            with open(filename, "w", newline="") as file:
                file.write(name + "\n")
                writer = csv.writer(file)
                writer.writerows(series)
                file.write(artist + "\n")
                file.write(avatar)
            print(f"Saved Spotify Playlist data for {code} to {filename}")
        else:
            print(f"Not enough series available for song ID {code}.")

if __name__ == "__main__":
    main()
'''

'''
def main():
    with open("src/utils/songs", "r") as file:
        codes = file.read().splitlines()

    for code in codes:
        if code == '49gk6oeq':
            continue
        print(f"Processing song ID: {code}")
        series = get_tiktok_series(code)[1]
        name = get_tiktok_series(code)[0]
        artist = get_tiktok_series(code)[2]
        avatar = get_tiktok_series(code)[3]
        if series is None:
            print(f"No data found for {code}.")
            continue
        if len(series) > 0:
            filename = f"tiktok_series_{code}.csv"
          # write_csv(filename, series)
            with open(filename, "w", newline="") as file:
                file.write(name + "\n")
                writer = csv.writer(file)
                writer.writerows(series)
                file.write(artist)
                file.write("\n" + avatar)
            print(f"Saved Tiktok series data for {code} to {filename}")
        else:
            print(f"Not enough series available for song ID {code}.")

if __name__ == "__main__":
    main()
'''


def read_spotify_csv_files(folder):
    # Construct a file path pattern for CSV files in the folder
    csv_pattern = os.path.join(folder, '*.csv')
    csv_files = glob.glob(csv_pattern)
    print(csv_pattern)
    
    # Dictionary to store the DataFrames
    dataframes = {}
    
    for file in csv_files:
        try:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file)
            # Use the base file name (e.g., "data.csv") as the key
            dataframes[os.path.basename(file)] = df
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    return dataframes


'''
if __name__ == "__main__":
    csv_data = read_spotify_csv_files('spotify_reach_dataset')
    for filename, df in csv_data.items():
        print(f"Contents of {filename}:")
        print(df.head())
'''

def read_csv_file(folder, code):
    file_name = f"spotify_playlist_series_{code}.csv"
    file_path = os.path.join(folder, file_name)
    print(file_path)
        
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        # Use the base file name (e.g., "data.csv") as the key
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


#spotify_playlists_dataset/spotify_playlist_series_nv4xpgkm.csv

#print(read_csv_file('spotify_playlists_dataset', 'nv4xpgkm'))

def parse_spotify_playlist_csv(file_id):
    # Construct file name and full file path
    file_name = f"spotify_playlist_series_{file_id}.csv"
    file_path = os.path.join('spotify_playlists_dataset', file_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        
        if len(lines) < 3:
            raise ValueError("CSV file does not have the expected structure.")
        
        # Extract the components based on the assumed file structure
        playlist_title = lines[0]
        artist = lines[-2]
        image_url = lines[-1]
        
        # Data rows are assumed to be between the first and the last two lines
        data_lines = lines[1:-2]
        data = []
        for line in data_lines:
            parts = line.split(',')
            if len(parts) == 2:
                try:
                    timestamp = int(parts[0])
                    value = int(parts[1])
                    data.append((timestamp, value))
                except ValueError:
                    print(f"Skipping invalid data row: {line}")
            else:
                print(f"Skipping line with unexpected format: {line}")
        
        # Convert data rows to a DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'value'])
        
        return {
            0: playlist_title,
            1: df,
            2: artist,
            3: image_url
        }
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    result = parse_spotify_playlist_csv('nv4xpgkm')
    if result:
        print("Playlist Title:", result[0])
        print("Artist:", result[2])
        print("Image URL:", result[3])
        print(result[1].head())


def parse_spotify_reach_csv(file_id):
    # Construct file name and full file path
    file_name = f"spotify_reach_series_{file_id}.csv"
    file_path = os.path.join('spotify_reach_dataset', file_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        
        if len(lines) < 3:
            raise ValueError("CSV file does not have the expected structure.")
        
        # Extract the components based on the assumed file structure
        playlist_title = lines[0]
        artist = lines[-2]
        image_url = lines[-1]
        
        # Data rows are assumed to be between the first and the last two lines
        data_lines = lines[1:-2]
        data = []
        for line in data_lines:
            parts = line.split(',')
            if len(parts) == 2:
                try:
                    timestamp = int(parts[0])
                    value = int(parts[1])
                    data.append((timestamp, value))
                except ValueError:
                    print(f"Skipping invalid data row: {line}")
            else:
                print(f"Skipping line with unexpected format: {line}")
        
        # Convert data rows to a DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'value'])
        
        return {
            0: playlist_title,
            1: df,
            2: artist,
            3: image_url
        }
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


if __name__ == "__main__":
    result = parse_spotify_reach_csv('nv4xpgkm')
    if result:
        print("Playlist Title:", result[0])
        print("Artist:", result[2])
        print("Image URL:", result[3])
        print(result[1].head())



def parse_tiktok_series_csv(file_id):
    # Construct file name and full file path
    file_name = f"tiktok_series_{file_id}.csv"
    file_path = os.path.join('tiktok_series_dataset', file_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        
        if len(lines) < 3:
            raise ValueError("CSV file does not have the expected structure.")
        
        # Extract the components based on the assumed file structure
        playlist_title = lines[0]
        artist = lines[-2]
        image_url = lines[-1]
        
        # Data rows are assumed to be between the first and the last two lines
        data_lines = lines[1:-2]
        data = []
        for line in data_lines:
            parts = line.split(',')
            if len(parts) == 2:
                try:
                    timestamp = int(parts[0])
                    value = int(parts[1])
                    data.append((timestamp, value))
                except ValueError:
                    print(f"Skipping invalid data row: {line}")
            else:
                print(f"Skipping line with unexpected format: {line}")
        
        # Convert data rows to a DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'value'])
        
        return {
            0: playlist_title,
            1: df,
            2: artist,
            3: image_url
        }
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


if __name__ == "__main__":
    result = parse_tiktok_series_csv('nv4xpgkm')
    if result:
        print("Playlist Title:", result[0])
        print("Artist:", result[2])
        print("Image URL:", result[3])
        print(result[1].head())