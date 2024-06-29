from flask import Flask,url_for,render_template,request,redirect
import csv
from dotenv import load_dotenv
import pandas as pd
import requests as re
import base64
import json
import os
from pyowm import OWM
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

app=Flask(__name__)


load_dotenv()

previous_tracks = []

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
owm_api_key = os.getenv("OWM_API_KEY")
scope = "playlist-modify-public playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope
))
user_id = sp.current_user()["id"]

def write_file(data):
    with open('feedback.csv','a+',newline='') as database:
        name = data['name']
        subject=  data['subject']
        message = data['message']
        cursor=csv.writer(database, delimiter = ',',quotechar='|')
        file=  cursor.writerow([name,subject,message])

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    result = re.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    access_token = json_result["access_token"]
    return access_token
def get_auth_header(token):
    return {
        "Authorization": "Bearer " + token
    }
def get_weather(location):
    owm = OWM(owm_api_key)
    mgr = owm.weather_manager()
    re.adapters.DEFAULT_RETRIES = 5
    re.adapters.DEFAULT_TIMEOUT = 10
    observation = mgr.weather_at_place(location)
    weather = observation.weather
    return weather
def get_recommendations(token, weather, previous_tracks=[]):
    url = "https://api.spotify.com/v1/recommendations"
    headers = get_auth_header(token)
    status=weather.detailed_status.lower()
    status=status.split(" ")
    weather_seeds = {
        "clear": {
        "seed_genres": ["pop", "dance"],
        "target_energy": [0.6, 0.8]
        },
        "few clouds": {
            "seed_genres": ["pop", "dance", "indie pop"],
            "target_energy": [0.5, 0.7]
        },
        "scattered clouds": {
            "seed_genres": ["pop", "alternative", "folk"],
            "target_energy": [0.4, 0.6]
        },
        "broken clouds": {
            "seed_genres": ["indie pop", "alternative", "soft rock"],
            "target_energy": [0.3, 0.5] 
        },
        "overcast clouds": {
            "seed_genres": ["chillhop", "lofi", "ambient"],
            "target_energy": [0.2, 0.4] 
        },
        "light rain": {
            "seed_genres": ["acoustic", "folk", "indie"],
            "target_energy": [0.3, 0.5]  
        },
        "moderate rain": {
            "seed_genres": ["rainy day", "lofi", "instrumental"],
            "target_energy": [0.2, 0.4] 
        },
        "heavy rain": {
            "seed_genres": ["rainy day", "ambient", "classical"],
            "target_energy": [0.1, 0.3] 
        },
        "extreme rain": {
            "seed_genres": ["storm ambience", "soundtracks"],
            "target_energy": [0.4, 0.6] 
        },
        "light snow": {
            "seed_genres": ["winter vibe", "acoustic", "instrumental"],
            "target_energy": [0.1, 0.3]  
        },
        "heavy snow": {
            "seed_genres": ["winter vibe", "classical", "ambient"],
            "target_energy": [0.05, 0.2] 
        },
        "mist": {
            "seed_genres": ["ambient", "drone", "classical"],
            "target_energy": [0.1, 0.25] 
        },
        "smoke": {
            "seed_genres": ["ambient", "drone", "dark ambient"],
            "target_energy": [0.1, 0.2] 
        },
        "fog": {
            "seed_genres": ["ambient", "classical", "soundtracks"],
            "target_energy": [0.05, 0.2] 
        },
        "haze": {
            "seed_genres": ["lofi", "electronic", "chillwave"],
            "target_energy": [0.2, 0.4] 
        },
        "thunderstorm": {
            "seed_genres": ["rock", "alternative rock", "soundtracks"],
            "target_energy": [0.5, 0.7] 
        },
        "tornado": {
            "seed_genres": ["storm ambience", "soundtracks"],
            "target_energy": [0.6, 0.8] 
        }
    }
    if weather.detailed_status.lower() in weather_seeds:
        seeds = weather_seeds[weather.detailed_status.lower()]
        data = {
            "seed_genres": seeds.get("seed_genres"),
            "target_energy": seeds.get("target_energy"),
            "limit": 100,
            "min_popularity": 5,
            "max_popularity": 70
        }
        result = re.get(url, headers=headers, params=data)
        json_result = json.loads(result.content)
        tracks = json_result["tracks"]
        recommendations = random.sample(tracks, 50)
        return recommendations
    else:
        print(f"Weather condition not found: {weather.detailed_status}.")
        return None
def create_playlist(user_id, playlist_name, track_uris):
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
    playlist_id = playlist['id']
    sp.playlist_add_items(playlist_id, track_uris)
    print(f"Playlist '{playlist_name}' created successfully!\nKindly wait for few minutes for the playlist to showup in your account.")

def get_playlist(location):
    cities=pd.read_csv(r'.\Countries\cities.csv')
    token = get_token()
    previous_tracks = []
    city,country = location.split(',')
    country = cities[cities['country']==country]['iso2']
    location = city+','+country.iloc[0]
    weather = get_weather(location)
    recommendations = get_recommendations(token, weather, previous_tracks)
    if recommendations:
        print(f"Weather: {weather.detailed_status}")
        print("Recommended Playlist:")
        track_uris = []
        playlist_data = []
        for track in recommendations:
            print(f"Track: {track['name']} - {track['artists'][0]['name']}")
            print(f"  Link: {track['external_urls']['spotify']}")
            print("-" * 20)
            track_uris.append(track['uri'])
            playlist_data.append({
                "name": track['name'],
                "artist": track['artists'][0]['name'],
                "link": track['external_urls']['spotify']
            })
        return playlist_data,track_uris
    else:
        print("No recommendations found.")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)
@app.route('/submit_form',methods=['POST','GET'])
def submit():
    if request.method == "POST":
        data = request.form.to_dict()
        write_file(data)
        return redirect('thankyou.html')
    else:
        return 'things went wrong, try again'

@app.route('/playlist', methods=['POST','GET'])
def generate():
    if request.method=="POST":
        location = request.form['location']
        playlist_name = request.form['name']
        playlist_data,track_uris = get_playlist(location)
        create_playlist(user_id, playlist_name, track_uris)
        previous_tracks.extend(track_uris)
        if playlist_data:
            return render_template('playlist.html',playlist=playlist_data)
        else:
            return "No recommendations found."
    else:
        return 'things went wrong'
if __name__=='__main__':
    app.run()

