import os
from flask import Flask, request, redirect
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# load environment variables from .env
load_dotenv()

# initalize Flask app
app = Flask(__name__)

# initialize SpotifyOAuth and set permissions 
sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
    scope="user-top-read"
)

# stores spotify access token 
token_info = None

@app.route('/')
def index():
    return 'Server is running.'

@app.route('/login')
def login():
    # endpoint for user to log in to spotify
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # endpoint after user authorizes spotify
    global token_info
    # get authorization code from URL 
    code = request.args.get('code')
    if code:
        try:
            # exchange code for access token 
            token_info = sp_oauth.get_access_token(code)
            return redirect('/success')
        except:
            return "An error occurred during token exchange."
    return "Authorization code not found."

@app.route('/success')
def success():
    return "Authorization successful! You can now use the bot."

def get_spotify_token():
    # try to get a previously stored token, and if not there then ask user to authenticate
    global token_info
    token_info = sp_oauth.get_cached_token()

    if token_info is None:
        raise ValueError("Token info not found. Did you authenticate?")

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info['access_token']

def get_spotify_client():  
    # create spotipy client using token 
    from spotipy import Spotify
    token = get_spotify_token()
    return Spotify(auth=token)

if __name__ == "__main__":
    app.run(port=5000)
