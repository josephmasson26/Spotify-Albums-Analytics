# Spotify Playlist Analyzer
This is a simple application written in Python and HTML with Flask that uses Spotify's API and data plotting to analyze public Spotify playlists.

The app calculates album occurences in your Spotify playlist and generates a data plot and cover art collage that you can save and share.

## Installation
1. Clone the repository:
```
  git clone josephmasson26/Spotify-Playlist-Analytics
```
2. Navigate to the directory.
3. In the directory's terminal, install the required dependencies.
```
   pip install flask pandas matplotlib requests Pillow
```
4. Set the Flask App Environement variable.
- For Unix and MacOS:
``` export FLASK_APP=AlbumCounter ```
- For Windows CLI:
```set FLASK_APP=AlbumCounter ```
5. Run the flask app with the command ``` flask run ```

The app is now running in the development server. You can access it by navigating to ```http://localhost:5000``` in your browser.

## Using the Analyzer
- Make sure the playlist you input is public.
- You can find a link to your public playlist on its page in Spotify. (Share -> Copy Link to Playlist)
- Allow time for app to complete its analysis.
- You can download your plot or your collage from the page.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- This project was initially developed to see albums in my Spotify Wrapped Top 100, but I realized it had potential for any playlist.
- Inspired by and based off my work in Jupyter Notebook for Hacklytics 2024.

### Spotify Playlist Analytics - Developed Joseph Masson 2023
