import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
import config

from colorthief import ColorThief
from urllib.request import urlretrieve

from yeelight import Bulb
import time

username = config.spotifyId
scope = 'user-read-currently-playing'

try:
    token = util.prompt_for_user_token(username, scope, client_id=config.CLIENT_ID,
                                       client_secret=config.CLIENT_SECRET,
                                       redirect_uri=config.REDIRECT_URI)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, client_id=config.CLIENT_ID, 
                                       client_secret=config.CLIENT_SECRET,
                                       redirect_uri=config.REDIRECT_URI)

spotify_object = spotipy.Spotify(auth=token)


class CurrentState:
    def __init__(self, id, rgb):
        self.id = id
        self.color = rgb

    def set_current_state(self, id, rgb):
        self.id = id
        self.color = rgb


class Lamps:
    def __init__(self, color):
        self.bulb1 = Bulb(config.bulb1Ip)
        self.bulb2 = Bulb(config.bulb2Ip)
        self.bulb1.set_rgb(color[0], color[1], color[2])
        self.bulb2.set_rgb(color[0], color[1], color[2])

    def set_lamp_color(self, color):
        self.bulb1.set_rgb(color[0], color[1], color[2])
        self.bulb2.set_rgb(color[0], color[1], color[2])


def main_loop(current_state_obj, lamps):
    while True:
        song = fetch_now_playing_info()
        check_current_song(current_state_obj, lamps, song)
        time.sleep(1)


def check_current_song(current, lamps, song):
    if current.id != song[0]:
        current.set_current_state(song[0], song[1])
        print(song)
        lamps.set_lamp_color(song[1])
    else:
        pass


def fetch_now_playing_info():
    current_playing = spotify_object.current_user_playing_track()
    try:
        now_playing_image_url = current_playing.get('item').get('album').get('images')[0].get('url')
        now_playing_color = image_to_rgb(now_playing_image_url)
        now_playing_id = current_playing.get('item').get('id')
        return [now_playing_id, now_playing_color]
    except:
        time.sleep(3)
        return fetch_now_playing_info()


def image_to_rgb(source_image):
    urlretrieve(source_image, 'image.jpg')

    color_thief = ColorThief('image.jpg')

    # get the dominant color
    dominant_color = color_thief.get_color(quality=1)
    return dominant_color


currentState = CurrentState(fetch_now_playing_info()[0], fetch_now_playing_info()[1])

lamps = Lamps(currentState.color)

main_loop(currentState, lamps)
