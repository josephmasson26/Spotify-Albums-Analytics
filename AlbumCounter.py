from flask import Flask, request, render_template, redirect, url_for
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import requests
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import base64

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
    
    playlist_id = request.args.get('url', default = "", type = str)
    
    # Split the URL by the '/' character and get the part after 'playlist/'
    playlist_part = playlist_id.split('/')[-1]

    # Split this part by the '?' character to get the playlist ID
    playlist_id = playlist_part.split('?')[0]

    print(playlist_id)

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
    token_response.raise_for_status()  # Raises an exception if the request failed

    # Get the access token
    access_token = token_response.json()['access_token']

    # Define the URL and headers for the playlist request
    playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    playlist_headers = {"Authorization": f"Bearer {access_token}"}

    # Make the GET request for the playlist
    playlist_response = requests.get(playlist_url, headers=playlist_headers)
    playlist_response.raise_for_status()  # Raises an exception if the request failed

    # Extract the tracks from the playlist response
    tracks = playlist_response.json()['tracks']['items']


    # This section creates a simple LinkedList data structure to keep track of the albums and their counts.
    # It then loops through the tracks and increments the count of the album in the LinkedList.

    # Note that I discount albums if they have 2 or less songs in them, so that
    # singles don't show up in the collage.

    class Node:
        def __init__(self, album_title):
            self.album_title = album_title
            self.count = 1
            self.next = None

    class LinkedList:
        def __init__(self):
            self.head = None

        def increment(self, album_title):
            if not self.head:
                self.head = Node(album_title)
            else:
                current = self.head
                while current:
                    if current.album_title == album_title:
                        current.count += 1
                        return
                    if not current.next:
                        current.next = Node(album_title)
                        return
                    current = current.next

    # Initialize the LinkedList
    albums = LinkedList()

    

    # For each track
    for track in tracks[:]:
        # Extract the album ID
        album_id = track['track']['album']['id']

        # Make a GET request to the Spotify API to get the album details
        album_response = requests.get(f"https://api.spotify.com/v1/albums/{album_id}", headers=playlist_headers)

        # Extract the album title
        album_title = album_response.json()['name']

        # Make a GET request to the Spotify API to get the album's tracks
        album_tracks_response = requests.get(f"https://api.spotify.com/v1/albums/{album_id}/tracks", headers=playlist_headers)

        # If the album does not have more than 2 songs, remove the track from tracks
        if album_tracks_response.json()['total'] <= 2:
            tracks.remove(track)
        else:
            # Increment the count of the album in the LinkedList
            albums.increment(album_title)

    # Finally, this section handles the visualization of the data.
    # It converts the LinkedList to a DataFrame, sorts it, and plots it.
    # Feel free to alter the colors and the size of the plot to your liking!


    

    # Initialize an empty dictionary for album counts
    album_counts = {}

    # Set the current node to the head of the LinkedList
    current = albums.head

    # While the current node is not None
    while current:
        # Add the current node's album title and count to the dictionary
        album_counts[current.album_title] = current.count

        # Set the current node to the next node
        current = current.next

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(list(album_counts.items()), columns=['Album', 'Count'])

    # Sort the DataFrame by 'Count' in descending order
    df = df.sort_values('Count', ascending=False)

    # Create a color palette with alternating colors
    palette = sns.color_palette(["#1DB954", "#88D498"], len(df))

    # Change the background color and the color of the text
    sns.set_theme(style="darkgrid", rc={"axes.facecolor": "#191414", "axes.labelcolor": "black", "text.color": "black", "xtick.color": "black", "ytick.color": "black"})

    # Create a larger bar plot with seaborn
    plt.figure(figsize=(12, 12))
    sns.barplot(x='Count', y='Album', data=df, orient='h', palette=palette)
    plt.title('Occurence of Albums in Spotify Wrapped 2023 Top 100 Songs')

    # Add tick marks by increments of one
    plt.xticks(range(0, df['Count'].max() + 1, 1))
    fig = plt.gcf()
    canvas = FigureCanvas(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)

    # Encode the BytesIO object as a base64 string
    img_data = base64.b64encode(png_output.getvalue()).decode('utf8')

    # Render the HTML template and pass the base64 string to it
    return render_template('index.html', img_data=img_data)



if __name__ == '__main__':
    app.run(debug=True)