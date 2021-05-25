import pandas as pd
import folium
import os
import datetime as dt
import json
import matplotlib.pyplot as plt
from ipyleaflet import Map, Marker, Polyline
from folium.plugins import MarkerCluster

with open('C:/Users/alicj/Desktop/python/veturilo/rowery/20180304_000020.json') as bicycles:
    data = json.load(bicycles)

path = os.listdir(path="C:/Users/alicj/Desktop/python/veturilo/rowery")

files = []

for t in path:
    x = dt.datetime(int(t[0:4]), int(t[4:6]), int(t[6:8]),
                    int(t[9:11]), int(t[11:13]), int(t[13:15]))
    files.append((x, t))  # data w formacie datetime i nazwa pliku

files = sorted(files)


# nazwy wszystkich stacji
stations = data[0]["places"]
# print(stations)
# for i in range(len(stations)):
#     print(stations[i]['name'])

df = pd.DataFrame(stations)
df

# punkt początkowy mapy - współrzędne warszawy
map = folium.Map(location=[52.2298, 21.0118], zoom_start=10)

# dodawanie markerów
marker_cluster = MarkerCluster().add_to(map)

for i in range(0, len(df)):
    folium.Marker(
        location=[df.iloc[i]['lat'], df.iloc[i]['lng']],
        popup=df.iloc[i]['name'],
    ).add_to(marker_cluster)
map  # wyświetlenie mapy ze stacjami

# TRASA ROWERU


def where_is_bike(prn, bike):
    with open('/Users/alicj/Desktop/python/veturilo/rowery/' + prn) as bicycles:
        data = json.load(bicycles)
        if data == []:
            return 'brak danych'
        try:
            # Warszawa
            for i in range(len(data[0]['places'])):
                bikes = data[0]['places'][i]['bike_numbers']
                if bikes == None:
                    continue  # brak rowerów na stacji
                if str(bike) in bikes:
                    # zwraca współrzędne stacji
                    return (float(data[0]['places'][i]["lat"]), float(data[0]['places'][i]["lng"]))

                # Konstancin
            for i in range(len(data[1]['places'])):
                bikes = data[1]['places'][i]['bike_numbers']
                if bikes == None:
                    continue  # brak rowerów na stacji
                if str(bike) in bikes:
                    return (float(data[1]['places'][i]["lat"]), float(data[1]['places'][i]["lng"]))

        except:
            return ('Błąd nieznany w pliku {}}'.format(prn))
    return 'w użytku'


road = []  # tablica stacji na trasie roweru - tuple współrzędnych
bikeNumber = 25734
# przeszukujemy pliki
for prn in files:
    bike_position = where_is_bike(prn[1], bikeNumber)
    if bike_position in ["w użytku", "brak danych"]:
        continue
    if len(road) == 0:
        road.append(bike_position)
        continue
    if road[-1] == bike_position:
        continue

    road.append(bike_position)

center = (road[0][0], road[0][1])  # pierwszy punkt trasy

# ustawiamy środek mapy na pierwszy punkt trasy
m = Map(center=center, zoom=11)
line = Polyline(locations=[road], color="blue", fill=False)
m.add_layer(line)


for bike in road:
    marker = Marker(location=(bike[0], bike[1]))
    m.add_layer(marker)
m

# ____________________________________________________________________
# AKTYWNOSC WYKRESY

stationsData = df[["uid", "number", "lat", "lng", "name"]].copy()
stationsData


def find_index(uid, places):
    for i, st in enumerate(places):
        if st["uid"] == uid:
            return i
    # return "brak stacji"


def bikes_at_station(files, uid="2585259"):
    bikes_list = []
    for file in files:
        with open('/Users/alicj/Desktop/python/veturilo/rowery/' + file[1]) as jsons:
            data = json.load(jsons)
            if data == []:
                continue
            station_index = find_index(uid, data[0]['places'])
            if station_index == None:
                continue
            bikes = data[0]['places'][station_index]["bike_numbers"]

            if bikes == None:
                bikes = ""  # brak rowerów na stacji
            bikes_list.append((bikes, file[0]))
    return bikes_list


bikes_list = bikes_at_station(files, "2585259")


def rented_bikes(bikes_list):
    counter = 0
    rentals = []
    for i in range(1, len(bikes_list)):
        #         print(bike_list[i][0])
        bike_numbers = bikes_list[i - 1][0].split(",")

        for b in bike_numbers:
            if b not in bikes_list[i][0]:
                counter += 1
        rentals.append(counter)
        counter = 0

    return rentals


act = rented_bikes(bikes_list)
act

days = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]


def week_rentals(bike_list, act):

    def week_activity(day):
        filt = week_station_activity["dni tygodnia"] == day
        day_activity = week_station_activity[filt]
        return day_activity["wypożyczenia"].sum()

    times = [t[1] for t in bike_list][1:]

    week_station_activity = pd.DataFrame(
        {"czas": times, "wypożyczenia": act}, index=times)
    week_station_activity["dni tygodnia"] = week_station_activity["czas"].dt.day_name(
    )

    number_of_rentals = []
    for day in days:
        number_of_rentals.append(week_activity(day))

    return number_of_rentals


week_rentals(bikes_list, act)


def total_week_rentals(stationsData, files):

    col = list(stationsData.columns)
    col.extend(days)
    df = pd.DataFrame(columns=col)

    for uid in stationsData["uid"]:
        bikes_list = bikes_at_station(files, uid)
        act = rented_bikes(bikes_list)
        week_act = week_rentals(bikes_list, act)

        row = list(stationsData.loc[len(df)])
        row.extend(week_act)
        df.loc[len(df)] = row

    return df


stationsData.iloc[:10]
total_week_rentals(stationsData, files)
# ===============================================================

# def getStations(file):
#     with open('/Users/alicj/Desktop/python/veturilo/rowery/' + file[1]) as jsons:
#         data = json.load(jsons)

#         stations = data[0]["places"]
#         df = pd.DataFrame(stations)
#     return df[["uid", "number", "lat", "lng", "name" "bike_numbers"]].copy()


# def initialList(file):
#     df = getStations(files[0])
#     return df[["uid", "bike_numbers"]].copy()

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

                n = df.loc[uid, "Monday"]
                n += rented_bikes_num(bikes, old_bikes)
                df.loc[uid, "Monday"] = n

                # print(n)

                # print(df.head())

                initialBikesList.loc[uid, "bike_numbers"] = bikes
                # return

                # initialBikesList = bikes

    return df


bikes(files)


# ================================================================

# def station_list():  # wspołrzędne stacji zbierac gdzies tam
#     tableStations = []
#     for prn in files:
#         prn = prn[1]
#         with open('/Users/alicj/Desktop/python/veturilo/rowery/' + prn) as s:
#             data = json.load(s)
#         if data == []:
#             continue
#         try:
#             for i in range(len(data[0]['places'])):
#                 station = data[0]['places'][i]['number']
#                 tableStations.append(station)
#             # tableStations = set(tableStations)

#         except:
#             pass
#         print(set(tableStations))
#     return set(tableStations)


# print(station_list())


# def func():
#     stat_ind = []
#     global df
#     for file in files:
#         with open('C:/Users/alicj/Desktop/python/veturilo/rowery/' + file[1]) as bicycles:
#             data = json.load(bicycles)
#             stations = data[0]["places"]
#             df = pd.DataFrame(stations)

#         return df
#    # for x in range(len(df)-2):
#       #  stat_ind.append(x)
#     # tablica stat_ind służyła mi tylko do sprawdzenia poprawności otrzymanych danych (ilość i numery indeksów)
#     print(stat_ind[:])


# index = func()  # 349

# print(len(df)-5)   #sprawdzam jaką liczbę zwróci mi program, by być pewna, że zgadza się z ilością indeksów - stacji

# jakie rowery są w jakim pliku na stacji o indeksie 0
# bt = bikes_at_station(files)

# rozpoczynamy badania aktywności na stacjach - wypożyczone rowery oraz oddane na stacje
# activity = []
# taken_from_stations = []
# given_to_stations = []

# count = 0  # zliczanie rowerów wypożyczonych ze stacji o indeksie w
# counter = 0  # zliczanie rowerów oddanych do stacji o indeksie w
# w = 0  # indeks stacji z pliku json


# def bikes_list(prn, stationName):
#     with open('/Users/alicj/Desktop/python/veturilo/rowery/' + prn) as bicycles:
#         data = json.load(bicycles)
#         if data == []:
#             return []  # 'brak danych'
#         for i in range(len(data[0]['places'])):
#             if data[0]['places'][i]["name"] == stationName:
#                 indexStation = i
#                 bikes = data[0]['places'][indexStation]['bike_numbers'].split(
#                     ",")
#                 print(bikes)
#             # try:

#                 if bikes == None:
#                     pass  # brak rowerów na stacji
#                 return (bikes, stationName, prn)
#         # except:
#         #     return ('Błąd nieznany w pliku {}'.format(prn))


# bikes_list("20180304_000020.json", 'Żelazna - Chłodna')


# def rented_or_parked(bikes_prn1, bikes_prn2):
#     # prn1 = bikes_activity()
#     rented = [x for x in bikes_prn1 if x not in bikes_prn2]
#     parked = [x for x in bikes_prn2 if x not in bikes_prn1]
#     return len(rented), len(parked)


# def station_activity(stationName):
#     rentedList = []
#     parkedList = []
#     dates = []
#     for i, prn in enumerate(files):
#         date = prn[0]
#         # tu chodzi o tuple files (data i nazwa pliku), chcemy nazwe
#         prn = prn[1]
#         # for j in range(len(prn)):
#         bikes_prn = bikes_list(prn, stationName)
#         # print(bikes_prn)
#         if i == 0:
#             bikes_prn1 = bikes_prn
#             continue

#         bikes_prn2 = bikes_prn
#         # print(bikes_prn1, bikes_prn2)
#         r, p = rented_or_parked(bikes_prn1, bikes_prn2)
#         rentedList.append(r)
#         parkedList.append(p)
#         dates.append(date)
#         bikes_prn1 = bikes_prn2
#     return (dates, rentedList, parkedList)


# # indexStation = 0

# # station_activity(indexStation)

# stationActivity = pd.DataFrame(station_activity('Żelazna - Chłodna')).T
# stationActivity


# def station_list():  # wspołrzędne stacji zbierac gdzies tam
#     tableStations = []
#     for prn in files:
#         prn = prn[1]
#         with open('/Users/alicj/Desktop/python/veturilo/rowery/' + prn) as s:
#             data = json.load(s)
#         # if data == []:
#         #     return []
#         try:
#             for i in range(len(data[0]['places'])):
#                 station = data[0]['places'][i]['name']
#                 tableStations.append(station)
#             # tableStations = set(tableStations)

#         except:
#             pass
#     return set(tableStations)


# # print(set(tableStations))
# # stationList = set(tableStations)
# # station_list()
# stationList = station_list()
# print(stationList)


# def create_df():
#     # tab = []
#     for station in stationList:
#         print(station)
#         # stationActivity = pd.DataFrame(station_activity(station)).T
#         station_activity(station)
#         # tab.append(a)
#         # return print(tab)


# create_df()


# def create_df():


# for w in range(0, len(df)):
#     count =0
#     counter = 0
#     n = 0
#     station_count = 0
#     stat_count2 = 0
#     tab = []

#     for nn in range(0, len(bt)):
#         bike_list = bt[n][w]
#         bike_list
#         tab.append([n,bike_list[0],bike_list[1]])
#         n+=1

#     #Zliczanie wypożyczonych rowerów na stacji 'w'

#     for mn in range(0, len(bt)):
#         bikes_then = tab[mn][2].split(",")
#         bikes_now = tab[mn+1][2].split(",")

#         for c in bikes_then:
#             if c not in bikes_now:
#                 count += 1

#         station_count += count
#         count = 0
#     taken_from_stations.append([w, station_count])

#     #Zliczanie oddanych rowerów na stacji 'w'

#     for i in range(0, len(bt)):
#         bike_numbers = tab[i][2].split(",")

#         for b in bike_numbers:
#             if b not in tab[i - 1][2]:
#                 counter += 1


#         stat_count2 += counter
#         counter = 0
#     given_to_stations.append([w,stat_count2])
#     #print(given_to_stations[:])

#     activity.append([w, given_to_stations[w][1]+taken_from_stations[w][1]])


# #print(activity)
# #print(taken_from_stations)


# #Sprawdzanie największej i najmniejszej aktywności na stacjach, a także dla informacji dodatkowej wypożyczeń i zwrotów
# def maks(function):
#     k = 0
#     for l in range(len(df)-5):
#         r = function[l][1]
#         if r > k:
#              k = r

#     print('największa ilość:',k)

# def min(function):
#     k = 0
#     for l in range(len(df)-5):
#         r = function[l][1]
#         if r < k:
#             k = r

#     print('najmniejsza ilość:',k)


# print('aktywność:')
# maks(activity)
# min(activity)

# print('\nwypożyczenia:')
# maks(taken_from_stations)
# min(taken_from_stations)

# print('\nzwrot rowerów na stację:')
# maks(given_to_stations)
# min(given_to_stations)
