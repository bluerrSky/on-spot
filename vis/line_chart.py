import pyrebase
import time
import seaborn as sns
import plotly.graph_objects as go
from collections import OrderedDict
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime,timedelta,date
import matplotlib.dates as mdates
firebaseConfig = {"apiKey": "AIzaSyCtsyPVafpy8fYU_d0tw2siZMVUIRM7_mE",
  "authDomain": "spotistats-e0200.firebaseapp.com",
  "projectId": "spotistats-e0200",
  "storageBucket": "spotistats-e0200.appspot.com",
  "messagingSenderId": "393837467502",
  "appId": "1:393837467502:web:aa8491f086d7eda6d8d37f",
  "measurementId": "G-H7PG869RL8",
  "databaseURL":"https://spotistats-e0200-default-rtdb.firebaseio.com/"
  }
# firebaseConfig = spotify_stats_current.firebaseConfig
print("Initializing Firebase database...")
successful = False
error = False
while not successful:
    try:
        firebase= pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()
        print("Database initialized!")
        successful = True
        error = False
    except Exception as e:
        print(f"UNSUCCESSFUL! ERROR:{e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
        error = True
data = db.child('tracks').get().val()

date_with_tracks = []
n_songs_date = {}
total_songs_played = 0
for track in data:
    track_info = data[track]
    song_duration = track_info["duration"]
    total_songs_in_date = len(track_info["time_played_at_list"])
    total_songs_played += total_songs_in_date
    for item_date in track_info['time_played_at_list']:
        d_ate,_time = item_date.split(" ")
        n_songs_date[str(d_ate)] = n_songs_date.get(str(d_ate),0)+1

data = dict(sorted(OrderedDict(n_songs_date).items(),key=lambda x:x[0]))
print(data)
def convert_str_to_object(date_string):
    date_object = datetime.strptime(date_string, '%Y-%m-%d')
    date_object = date(date_object.year, date_object.month, date_object.day)
    return date_object
start_date = min(data.keys())
end_date = max(data.keys())
print(f"the start date is {start_date}")
start_date = convert_str_to_object(start_date)
end_date = convert_str_to_object(end_date)
delta = timedelta(days=1)
current_date = start_date
dates = []
while current_date <= end_date:
    dates.append(current_date.strftime("%Y-%m-%d"))
    current_date += delta
updated_data = {}
for date in dates:
    if not date in data:
        data[date] = 0
data = dict(sorted(OrderedDict(data).items(),key=lambda x:x[0]))
sum_list = []
played_number_list = [item for item in data.values()]
print(played_number_list)
i = 0
for number in played_number_list:
    sum_list.append(sum(played_number_list[:i]))
    i += 1
print(sum_list)
x = [item for item in data.keys()]
y = sum_list
fig = go.Figure(data=go.Scatter(x=x,y=y,mode="lines+markers",name="songs played"))

fig.update_layout(title="Songs played",xaxis_title="date",yaxis_title="Count(songs)")
#for i in range(len(x)):
#    fig.add_annotation(x=x[i],y=y[i],text=f"({x[i]},{y[i]})",hovertext=f"({x[i]},{y[i]})",hoverlabel=dict(bgcolor="white",font_size=16),xref="x",yref="y",xanchor="center",yanchor="bottom")
fig.show()
