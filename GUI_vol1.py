import io
import os
import sys
import pandas as pd
import folium
import datetime as dt
import matplotlib.pyplot as plt
from ipyleaflet import Map, Marker, Polyline
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
import json
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

df = pd.DataFrame(stations)
df


def show_stations():
    m = folium.Map(
        location=[52.2298, 21.0118], tiles="Stamen Terrain", zoom_start=10
    )

    marker_cluster = MarkerCluster().add_to(m)

    for i in range(0, len(df)):
        folium.Marker(
            location=[df.iloc[i]['lat'], df.iloc[i]['lng']],
            popup=df.iloc[i]['name'],
        ).add_to(marker_cluster)
    return m


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


def bike_road(bikeNumber=25734):
    road = []  # tablica stacji na trasie roweru - tuple współrzędnych

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
    m = folium.Map(
        location=[52.2298, 21.0118], tiles="Stamen Terrain", zoom_start=12
    )
    line = folium.PolyLine([road], color="blue", fill=False)
    line.add_to(m)

    # for bike in road:
    #     marker = folium.Marker(location=(bike[0], bike[1]))
    # m.add_layer(marker)
    return m


bike_road()


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

    def initWindow(self):
        self.setWindowTitle(self.tr("Mapa folium"))
        self.setFixedSize(1500, 800)
        self.buttonUI()

    def buttonUI(self):
        shortPathButton = QtWidgets.QPushButton(self.tr("button"))
        button2 = QtWidgets.QPushButton(self.tr("button1"))
        button3 = QtWidgets.QPushButton(self.tr("button2"))

        shortPathButton.setFixedSize(120, 50)
        button2.setFixedSize(120, 50)
        button3.setFixedSize(120, 50)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(50, 50, 50, 50)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QHBoxLayout(central_widget)

        button_container = QtWidgets.QWidget()
        vlay = QtWidgets.QVBoxLayout(button_container)
        vlay.setSpacing(20)
        vlay.addStretch()
        vlay.addWidget(shortPathButton)
        vlay.addWidget(button2)
        vlay.addWidget(button3)
        vlay.addStretch()
        lay.addWidget(button_container)
        lay.addWidget(self.view, stretch=1)

        m = bike_road(25734)

        data = io.BytesIO()
        m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())


if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())
