import os
import discord
from dotenv import load_dotenv
from spotify_auth import get_spotify_client, sp_oauth

# load environment variables from .env and the discord token 
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# set up permissions for discord bot 
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# stores spotify client after authentication 
spotify = None

@client.event
async def on_ready():
    # event handler for when the discord bot connects to discord
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    # event handler when a message is sent on discord
    global spotify

    # ignore messages sent by bot
    if message.author == client.user:
        return

    if message.content.startswith('$help'):
        await message.channel.send("$login -> $auth -> $songs or $artists")

    if message.content.startswith('$login'):
        auth_url = sp_oauth.get_authorize_url()
        await message.channel.send(f"Authorize the application: {auth_url}")

    # bot gets access token after user authenticates and gets spotify client with token 
    if message.content.startswith('$auth'):
        try:
            spotify = get_spotify_client()
            await message.channel.send("Spotify authentication successful.")
        except ValueError:
            await message.channel.send("Authentication failed, please try again.")

    if message.content.startswith('$songs'):
        # check if user authenticated with spotify 
        if spotify is None:
            await message.channel.send("Authenticate first using $login and $auth.")
            return

        results = spotify.current_user_top_tracks(limit=25)

        response = "Your top 25 songs are:\n"
        for idx, item in enumerate(results['items']):
            song = item['name']
            artist = item['artists'][0]['name']
            response += f"{idx+1}. {song} by {artist}\n"

        await message.channel.send(response)

    if message.content.startswith('$artists'):
        if spotify is None:
            await message.channel.send("Authenticate first using $login and $auth.")
            return

        results = spotify.current_user_top_artists(limit=25)

        response = "Your top 25 artists are:\n"
        for idx, item in enumerate(results['items']):
            artist = item['name']
            response += f"{idx+1}. {artist}\n"

        await message.channel.send(response)

# run discord bot with my token 
client.run(TOKEN)
