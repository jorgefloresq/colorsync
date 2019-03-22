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
    token = util.prompt_for_user_token(username, scope, client_id= config.CLIENT_ID,
                                       client_secret= config.CLIENT_SECRET,
                                       redirect_uri= config.REDIRECT_URI)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, client_id=config.CLIENT_ID, 
                                       client_secret=config.CLIENT_SECRET,
                                       redirect_uri=config.REDIRECT_URI)

spotifyObject = spotipy.Spotify(auth=token)

class CurrentState:
    def __init__(self, id, rgb):
        self.id = id
        self.color = rgb

    def setCurrentState(self, id, rgb):
        self.id = id
        self.color = rgb

class Lamps:
    def __init__(self, color):
        self.bulb1 = Bulb(config.bulb1Ip)
        self.bulb2 = Bulb(config.bulb2Ip)

        self.bulb1.set_rgb(color[0], color[1], color[2])
        self.bulb2.set_rgb(color[0], color[1], color[2])

    def setLampColor(self, color):
        self.bulb1.set_rgb(color[0], color[1], color[2])
        self.bulb2.set_rgb(color[0], color[1], color[2])

def mainLoop(currentStateObj, lamps):
    while True:
        song = fetchNowPlayingInfo()
        checkCurrentSong(currentStateObj, lamps, song)
        time.sleep(1)

def checkCurrentSong(current, lamps, song):
    if current.id != song[0]:
        current.setCurrentState(song[0], song[1])
        print(song)
        lamps.setLampColor(song[1])
    else:
        pass

def fetchNowPlayingInfo():
    currentPlaying = spotifyObject.current_user_playing_track()
    try:
        nowPlayingImageURL = currentPlaying.get('item').get('album').get('images')[0].get('url')
        nowPlayingColor = imageToRGB(nowPlayingImageURL)
        nowPlayingId = currentPlaying.get('item').get('id')
        return [nowPlayingId, nowPlayingColor]
    except:
        time.sleep(3)
        return fetchNowPlayingInfo()


def imageToRGB(sourceImage):
    urlretrieve(sourceImage, 'image.jpg')

    color_thief = ColorThief('image.jpg')

    # get the dominant color
    dominant_color = color_thief.get_color(quality=1)
    return dominant_color

currentState = CurrentState(fetchNowPlayingInfo()[0],fetchNowPlayingInfo()[1])

lamps = Lamps(currentState.color)

mainLoop(currentState, lamps)