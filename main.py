import discord
from discord.ext import commands
import youtube_dl
from yt_dlp import YoutubeDL
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# Discord bot settings
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

# Spotify API credentials (Tạo ứng dụng tại https://developer.spotify.com/dashboard/)
with open("ci.txt", "r") as file:
    SPOTIFY_CLIENT_ID = file.read()
with open("cs.txt", "r") as file:
    SPOTIFY_CLIENT_SECRET = file.read()

spotify = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
))

# Play music command
@bot.command()
async def play(ctx, *, url_or_query):
    # Join voice channel
    if not ctx.author.voice:
        await ctx.send("Bạn phải tham gia voice channel trước!")
        return
    
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    # Handle Spotify links
    if "open.spotify.com" in url_or_query:
        try:
            # Extract track info
            track_id = url_or_query.split("/")[-1].split("?")[0]
            track = spotify.track(track_id)
            query = f"{track['name']} {track['artists'][0]['name']}"
            await ctx.send(f"Tìm kiếm trên YouTube: {query}")
        except Exception as e:
            await ctx.send("Không thể lấy thông tin từ Spotify link!")
            return
    else:
        query = url_or_query

    # Search and download from YouTube
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
            await ctx.send(f"Đang phát: {title}")
        except Exception as e:
            await ctx.send("Không thể tìm bài hát trên YouTube!")
            return

    # Play the audio
    voice_client = ctx.voice_client
    voice_client.stop()  # Stop any current audio
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }
    voice_client.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS))

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Đã dừng phát nhạc và rời kênh!")
    else:
        await ctx.send("Bot không ở trong voice channel nào!")

# Bot token
with open("dtoken.txt", "r") as file:
    TOKEN = file.read()
bot.run(TOKEN)
