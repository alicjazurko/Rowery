import pandas as pd
import folium
import os
import datetime as dt
import json

#Otwarcie pojedynczego pliku json
with open('C:/Users/alicj/Desktop/python/veturilo/rowery/20180304_000020.json') as bicycles:
    data = json.load(bicycles)

path = os.listdir(path="C:/Users/alicj/Desktop/python/veturilo/rowery")

files = []

for t in path:
    x = dt.datetime(int(t[0:4]), int(t[4:6]), int(t[6:8]),
                    int(t[9:11]), int(t[11:13]), int(t[13:15]))
    files.append((x, t))  # data w formacie datetime i nazwa pliku

files = sorted(files)


def initialStationData(data):
    stations = data[0]["places"]
    df = pd.DataFrame(stations)
    df = df[["uid", "number", "lat", "lng", "name"]].copy()
    df["Monday"] = [0] * len(df)
    df["Tuesday"] = [0] * len(df)
    df["Wednesday"] = [0] * len(df)
    df["Thursday"] = [0] * len(df)
    df["Friday"] = [0] * len(df)
    df["Saturday"] = [0] * len(df)
    df["Sunday"] = [0] * len(df)
    df = df.set_index("uid")
    return df

#Funkcja zliczająca wypożyczone rowery
def rented_bikes_num(new_bikes_list, old_bikes_list):
    counter = 0
    # if not bool(new_bikes_list) or not bool(old_bikes_list): return 0
    if new_bikes_list == None:
        new_bikes_list = ""
    if old_bikes_list == None:
        return 0

    if "," not in old_bikes_list:
        old = old_bikes_list
    else:
        old = old_bikes_list.split(",")

    try:
        for bikes in old:
            if bikes not in new_bikes_list:
                counter += 1
    except:
        print(old_bikes_list)

    return counter

#Funkcja pobierająca podstawowe dane o stacjach i aktywności na nich dla wszystkich dni tygodnia po kolei
def bikes(files):

    for i, file in enumerate(files):
        with open('/Users/alicj/Desktop/python/veturilo/rowery/' + file[1]) as jsons:
            data = json.load(jsons)
            if data == []:
                continue

            if i == 0:
                df = initialStationData(data)
                stations = data[0]["places"]
                initialBikesList = pd.DataFrame(stations)
                initialBikesList = initialBikesList[[
                    "uid", "bike_numbers"]].copy()
                initialBikesList = initialBikesList.set_index("uid")
                continue

            for station in data[0]['places']:
                bikes = station["bike_numbers"]
                uid = station["uid"]
                if uid not in initialBikesList.index:
                    continue
                # old_bikes = list(initialBikesList.loc[uid])[0]
                old_bikes = initialBikesList.loc[uid, "bike_numbers"]
                # print(list(old_bikes)[0].split(","))

                dayOfWeek = file[0].weekday()

                if dayOfWeek == 0:
                    n = df.loc[uid, "Monday"]
                    n += rented_bikes_num(bikes, old_bikes)
                    df.loc[uid, "Monday"] = n
                elif dayOfWeek == 1:
                    n = df.loc[uid, "Tuesday"]
                    n += rented_bikes_num(bikes, old_bikes)
                    df.loc[uid, "Tuesday"] = n
                elif dayOfWeek == 2:
                    n = df.loc[uid, "Wednesday"]
                    n += rented_bikes_num(bikes, old_bikes)
                    df.loc[uid, "Wednesday"] = n
                elif dayOfWeek == 3:
                    n = df.loc[uid, "Thursday"]
                    n += rented_bikes_num(bikes, old_bikes)
                    df.loc[uid, "Thursday"] = n
                elif dayOfWeek == 4:
                    n = df.loc[uid, "Friday"]
                    n += rented_bikes_num(bikes, old_bikes)
                    df.loc[uid, "Friday"] = n
                elif dayOfWeek == 5:
                    n = df.loc[uid, "Saturday"]
                    n += rented_bikes_num(bikes, old_bikes)
                    df.loc[uid, "Saturday"] = n
                elif dayOfWeek == 6:
                    n = df.loc[uid, "Sunday"]
                    n += rented_bikes_num(bikes, old_bikes)
                    df.loc[uid, "Sunday"] = n

                initialBikesList.loc[uid, "bike_numbers"] = bikes
                # return

                # initialBikesList = bikes

    return df

#Zapisanie dataframe z funkcji bikes do zmiennej
weekActivity = bikes(files)

#utworzenie pliku json z informacjami o aktywności
weekActivity.to_json('C:/Users/alicj/Desktop/python/weekActivity.json')

with open('C:/Users/alicj/Desktop/python/weekActivity.json') as weekActivity:
    data = json.load(weekActivity)
    print(weekActivity)

#print(data)

dfAct = pd.DataFrame.from_dict(data, orient="columns")
#dfAct

#Sprawdzam zakres wypożyczeń do uwzględnienia
#Ta część nie musi być w głównym kodzie bo nic nie wnosi poza informacją dla mnie na początku 
#najwięcej wypożyczeń
taken = weekActivity['Sunday']
MAX = 0
for station in range(len(weekActivity)):
    if taken[station] > MAX:
        MAX = taken[station]
print(MAX)

#Najmniej wypożyczeń
MIN = 0
for station in range(len(weekActivity)):
     if taken[station] < MIN:
        MIN = taken[station]
print(MIN)


#Stworzenie funkcji wyświetlającej mapę aktywności w zależności od dnia tygodnia
def day_activity(day):
    
    #Tworzenie mapy
    m_act = folium.Map(location=[52.2298,21.0118], zoom_start=10)
    
    #pobranie wypożyczeń z danego dnia dla wszystkich stacji
    taken = weekActivity[day]  
    
    #Dodawanie markerów w zależności od aktywności stacji
    for i in range(len(weekActivity)): 
        
        #nie chciało zapisać popup dopóki wartości nie były typu string
        nr = str(weekActivity.iloc[i]['number'])
        nazwa = str(weekActivity.iloc[i]['name'])
        ilosc = str(weekActivity.iloc[i][day])
    
        if taken[i] > 300:  
            folium.Marker(
            location=[weekActivity.iloc[i]['lat'], weekActivity.iloc[i]['lng']],
            popup='stacja: ' + nr + '\n' + nazwa + '\naktywność: ' + ilosc,
            icon = folium.Icon(color="red",icon="angle-double-up", prefix='fa')
            ).add_to(m_act)
        if taken[i] in range(150,300):  
            folium.Marker(
            location=[weekActivity.iloc[i]['lat'], weekActivity.iloc[i]['lng']],
            popup='stacja: ' + nr + '\n' + nazwa + '\naktywność: ' + ilosc,
            icon = folium.Icon(color="orange",icon="angle-up", prefix='fa')
            ).add_to(m_act)
        if taken[i] in range(50,150):  
            folium.Marker(
            location=[weekActivity.iloc[i]['lat'], weekActivity.iloc[i]['lng']],
            popup='stacja: ' + nr + '\n' + nazwa + '\naktywność: ' + ilosc,
            icon = folium.Icon(color="blue",icon="angle-down", prefix='fa')
            ).add_to(m_act)
        if taken[i] in range(0,50):  
            folium.Marker(
            location=[weekActivity.iloc[i]['lat'], weekActivity.iloc[i]['lng']],
            popup='stacja: ' + nr + '\n' + nazwa + '\naktywność: ' + ilosc,
            icon = folium.Icon(color="darkblue",icon="angle-double-down", prefix='fa')
            ).add_to(m_act)
    return m_act

#Sprawdzam czy funkcja działa
day = "Saturday"
day_activity(day)


