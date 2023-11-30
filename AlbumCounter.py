from flask import Flask, request, abort, render_template, redirect, url_for, send_from_directory
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import os
import atexit
import glob

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Get the URL from the form
        url = request.form.get('url')
        # Redirect to the /plot route with the URL as a parameter
        return redirect(url_for('plot', url=url))
    return render_template('form.html')



@app.route('/plot', methods = ['GET', 'POST'])
def plot():
    #Split URL into the playlist ID
    url = request.args.get('url', default = "", type = str)
    playlist_id = url.split('/')[-1]
    if '?' in playlist_id:
        playlist_id = playlist_id.split('?')[0]

    if not playlist_id:
        return "Error: No playlist ID provided"


    # Define the URL, headers, and data for the token request
    token_url = "https://accounts.spotify.com/api/token"
    token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_data = {
        "grant_type": "client_credentials",
        "client_id": "66199634274347538430009f1d54f87e",
        "client_secret": "84c6c86940154d0e84e05ed1ae75d9ae",
    }

    # Make the POST request for the token
    token_response = requests.post(token_url, headers=token_headers, data=token_data)
    # token_response.raise_for_status()  # Raises an exception if the request failed

    # Get the access token
    access_token = token_response.json()['access_token']

    # Define the URL and headers for the playlist request
    playlist_url = "https://api.spotify.com/v1/playlists/" + playlist_id
    playlist_headers = {"Authorization": f"Bearer {access_token}"}

    # Make the GET request for the playlist
    playlist_response = requests.get(playlist_url, headers=playlist_headers)
    # playlist_response.raise_for_status()  # Raises an exception if the request failed

    # Check the status of the response
    if playlist_response.status_code != 200:
        print(f"Error: Spotify API request returned status code {playlist_response.status_code}")
        print(playlist_response.text)
    else:
        # Try to extract the tracks from the response
        try:
            tracks = playlist_response.json()['tracks']['items']
        except KeyError:
            print("Error: Response does not contain track items")
            print(playlist_response.json())

    # Note that I discount albums if they have 2 or less songs in them, so that
    # singles don't show up in the collage.

    # Initialize the dictionary
    albums = {}
    
    # Extract the album IDs
    album_ids = [track['track']['album']['id'] for track in tracks]

    # Split the album IDs into batches of 20 (the maximum allowed by the Spotify API)
    album_id_batches = [album_ids[i:i + 20] for i in range(0, len(album_ids), 20)]

    for album_id_batch in album_id_batches:
        # Join the album IDs with commas
        album_ids_str = ','.join(album_id_batch)

        # Make a GET request to the Spotify API to get the album details
        album_response = requests.get(f"https://api.spotify.com/v1/albums?ids={album_ids_str}", headers=playlist_headers)

        # The response will be a dictionary with an 'albums' key containing a list of album details
        for album in album_response.json()['albums']:
            # Extract the album title
            album_title = album['name']

            # Make a GET request to the Spotify API to get the album's tracks
            album_tracks_response = requests.get(f"https://api.spotify.com/v1/albums/{album['id']}/tracks", headers=playlist_headers)

            # If the album does not have more than 2 songs, remove the track from tracks
            if album_tracks_response.json()['total'] <= 2:
                tracks = [track for track in tracks if track['track']['album']['id'] != album['id']]
            else:
                # Increment the count of the album in the dictionary
                if album_title in albums:
                    albums[album_title] += 1
                else:
                    albums[album_title] = 1
    
    # Finally, this section handles the visualization of the data.
    # It converts the Dictionary to a DataFrame, sorts it, and plots it.
    # Feel free to alter the colors and the size of the plot to your liking!

    #Convert the dictionary to a DataFrame
    df = pd.DataFrame(list(albums.items()), columns=['Album', 'Count'])


    # Sort the DataFrame by 'Count' in descending order
    df = df.sort_values('Count', ascending=False)

    # Create a larger bar plot with seaborn
    plt.figure(figsize=(12, 12))
    plt.barh(df['Album'], df['Count'], color='blue')
    plt.gca().invert_yaxis()  # Invert y-axis to have the highest count at the top
    plt.xlabel('Count')
    plt.title('Occurence of Albums in Spotify Wrapped 2023 Top 100 Songs')

    # Add tick marks by increments of one
    plt.xticks(range(0, df['Count'].max() + 1, 1))
    
    plt.savefig('static/plot.png')

    return redirect(url_for('index'))

@app.route('/index')
def index():
    return render_template('index.html')

def clear_static_folder():
    files = glob.glob('./static/*')
    for f in files:
        if 'favicon.png' in f:
            continue
        elif 'github.png' in f:
            continue
        os.remove(f)
    
    return redirect(url_for('index'))

atexit.register(clear_static_folder)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        clear_static_folder()
