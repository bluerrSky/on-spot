import spotipy.util as util
import requests
from dateutil import parser
import time
import datetime
import traceback
import threading
import itertools
import pyrebase
import sys 
# import logging




#firebase credentials
from config import initialize_firebase, get_spotify_credentials


db = initialize_firebase()


spotify_credentials = get_spotify_credentials()

print("Firebase and Spotify configurations loaded!")



# def is_connected():
#     try:
#         response = requests.get("http://www.google.com")
#         if response.status_code == 200:
#             return True
#         else:
#             return False
#     except Exception:
#         return False




error = False
firebase= pyrebase.initialize_app(firebaseConfig)
db = firebase.database()




def get_access_token():
    access_token = util.prompt_for_user_token(username=username, 
                                    scope=scope, 
                                    client_id=client_id,   
                                    client_secret=client_secret,     
                                    redirect_uri=redirect_uri)



    #saving access token to firebase database
    token_data = access_token
    db.child("Token").set(token_data)



    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    return headers
info_dict = {}


# def get_recently_played(limit=50):
#     # global info_dict
#     played_tracks = []
#     for item in requests.get(f'https://api.spotify.com/v1/me/player/recently-played?limit={limit}',headers=headers).json()["items"]:

#         #this part gets the duration of the song played
#         played_tracks.append(item['track']['name'])
#         duration_ms = item['track']["duration_ms"] // 1_000
#         # info_dict[track_name] = duration_ms
#         track_URI = item['track']['uri']
#         track_artist = item['track']['artists'][0]['name']
#         #this part gets the time when the song was played


# def get_top_tracks_artists(choice = "tracks"):
#     timerange_list = ["short_term","long_term","medium_term"]

#     #this part gets the top artists of the user(short term)
#     top_things = {}
#     if choice == "artists" or "tracks":
#         for time in timerange_list:
#             sub_time_top = []
#             for item in requests.get(f'https://api.spotify.com/v1/me/top/{choice}?time_range={time}&limit=50',headers=headers).json()["items"]:
#                 sub_time_top.append(item['name'])
#             top_things[time] = sub_time_top
#     else:
#         return "INVALID REQUEST"
            
    # return top_things

headers = get_access_token()
#get currently playing song
def get_currently_playing(items="all"):
    global error
    global headers
    while True:
            try:
                response = requests.get("https://api.spotify.com/v1/me/player/currently-playing",headers=headers)
                if response.status_code == 401:
                    print("your access token has expired!")
                    headers = get_access_token()
                    error = True
                response = response.json()
                track_name = response['item']['name']
                track_artist = response['item']['artists'][0]['name']
                track_duration_seconds = response['item']['duration_ms'] / 1000
                track_progress_seconds = response['progress_ms'] / 1000
                track_uri = response['item']['uri']
                is_playing = response['is_playing']
                spotify_con = True
                error = False
                if items == "all":
                    return track_name,track_duration_seconds,track_progress_seconds,track_artist,is_playing,track_uri
                elif items == "progress":
                    return track_progress_seconds
            except Exception as e:
                if isinstance(e, TypeError) and str(e) == "'NoneType' object is not subscriptable":
                    print("\rAn ad is playing!",end="")
                    # traceback.print_exc()
                
                    # print(requests.get("https://api.spotify.com/v1/me/player/currently-playing",headers=headers).json())'
                elif isinstance(e,requests.exceptions.JSONDecodeError):
                    print("\rSpotify is closed & No song is playing!",end="")
                    sys.stdout.flush()
                else:
                    print("\rCONNECTION WITH SPOTIFY FAILED! retrying...",end="")
                    traceback.print_exc()
                    time.sleep(1)
                error = True

#program to check if computer is connected to internet


restart_n = 0
def remove_special(string):
  # Use the replace() method to remove full stops and commas
  return string.replace('.', '').replace(":","").replace("/","").replace("//","")


prev_song = None
start_time = None
buffer_time = None
while True:
    try:
        track_name, song_duration, track_progress,track_artist,is_playing,track_URI = get_currently_playing()
        track_name = remove_special(track_name)
        branch = "tracks"      

        if db.child(branch).child(track_name).get().val() is not None:
            total_time = db.child(branch).child(track_name).get().val()['total_time_played']
            db.child(branch).child(track_name).update({"prev_time":total_time}) 
        else:
            time_now = datetime.datetime.now()
            data ={"duration":song_duration,
            "no_of_times_played":1,
            "time_played_at":time_now.strftime('%Y-%m-%d %H:%M:%S'),
            "time_played_at_list":[time_now.strftime('%Y-%m-%d %H:%M:%S')],
            "total_time_played":0,
            "artist":track_artist,
            "track_URI":track_URI,
            # "track_progress":track_progress,
            "buffer_time":0,
            "prev_time":0}
            db.child(branch).child(track_name).set(data)
            print(f"\rNEW SONG ADDED!({track_name})",end="\n")
            # sys.stdout.flush()

        
        #WORKING ANIMATION
        anitons = ['|', '/', '-', '\\']
        def animate():
            for c in itertools.cycle(anitons):
                if error:
                    break

                print("\rWORKING " +c,end="\033[K")                    
                sys.stdout.flush()
                time.sleep(0.1)
        t = threading.Thread(target=animate)
        t.daemon = True
        t.start()



        if is_playing:
            if start_time is None:
                start_time = datetime.datetime.now()
                current_progress = get_currently_playing('progress')
                time_now = datetime.datetime.now()
                fire_time = db.child(branch).child(track_name).get().val()['time_played_at_list']
                fire_time_formatted = datetime.datetime.strptime(fire_time[-1],"%Y-%m-%d %H:%M:%S")
                condition_secs = (time_now - fire_time_formatted).total_seconds()
                # print(f"thiese are the condition secs {condition_secs}")
                if current_progress <= song_duration*0.08 and  condition_secs>= song_duration*0.6:
                    
                    db.child(branch).child(track_name).update({"time_played_at_list":fire_time+[time_now.strftime('%Y-%m-%d %H:%M:%S')]})
                    fire_no = db.child(branch).child(track_name).get().val()['no_of_times_played']
                    db.child(branch).child(track_name).update({'no_of_times_played':fire_no+1})
            if track_name != prev_song and prev_song != None:
                # prev_song = track_name
                elapsed_time = datetime.datetime.now() - start_time
                prev_songbuffer =db.child(branch).child(prev_song).get().val()['buffer_time']
                prev_songtime = db.child(branch).child(prev_song).get().val()['prev_time']
                # print(f"buffer time of {prev_song} is {prev_songbuffer}seconds and elapsed time is {elapsed_time} seconds and previously played time is {prev_songtime}")
                db.child(branch).child(prev_song).update({'total_time_played':elapsed_time.total_seconds()+prev_songtime+prev_songbuffer+7})
                start_time = None
                print(f"\rSONG UPDATED!({prev_song})",end="\n")
                # sys.stdout.flush()
        else:
            if start_time is not None:
                elapsed_time = datetime.datetime.now() - start_time
                db.child(branch).child(track_name).update({"buffer_time": elapsed_time.total_seconds()})
                start_time = None  
        prev_song = track_name
        # print(db.child(branch).child(track_name).get().val())
        error = False
        time.sleep(1)
    except Exception as e:
            error = True
            # print(f"the error is {e}")
            if isinstance(e,requests.exceptions.JSONDecodeError):
                print("\rSpotify is closed & No song is playing!",end="")
                sys.stdout.flush()
            elif isinstance(e, TypeError) and str(e) == "'NoneType' object is not subscriptable":
                print("\rAn ad is playing!",end="\033[K")
            else:
                traceback.print_exc()
                print("\rRetyring in 5s")
                time.sleep(5)
            
