import io
import os
import sys
from typing import Text
import pandas as pd
import folium
import datetime as dt
import matplotlib.pyplot as plt
from ipyleaflet import Map, Marker, Polyline
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
import json
from folium.plugins import MarkerCluster
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QDialog
from pyqtgraph import PlotWidget
import pyqtgraph as pg

# pobranie danych
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

# -------------------------------------------------------------------
# Rozmieszczenie stacji
# -------------------------------------------------------------------


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

# -------------------------------------------------------------------
# Trasa roweru
# -------------------------------------------------------------------

# funkcja pokazująca gdzie aktualnie jest rower (w którym pliku)


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

# funkcja wyznaczająca trasę roweru zwraca mapę


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
        location=center, tiles="Stamen Terrain", zoom_start=12
    )
    line = folium.PolyLine([road], color="blue", fill=False)
    line.add_to(m)

    # for bike in road:
    #     marker = folium.Marker(location=(bike[0], bike[1]))
    # m.add_layer(marker)
    return m

# -------------------------------------------------------------------
# wykres aktywności tygodniowej dla danej stacji
# -------------------------------------------------------------------


with open('C:/Users/alicj/Desktop/python/weekActivity.json') as weekActivity:
    data = json.load(weekActivity)

dfAct = pd.DataFrame.from_dict(data, orient="columns")


def plot_activity(stationName):

    days = ["Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"]

    dfAct1 = dfAct.loc[dfAct["name"] == stationName, days]
    dflist = dfAct1.values.tolist()

    plt.figure(num=str(stationName), figsize=(12, 6))
    plt.bar(days, dflist[0])
    plt.title("Aktywność tygodniowa na stacji")
    plt.show()


# -------------------------------------------------------------------
# Mapa aktywności wszystkich stacji w zależności od dnia tygodnia
# -------------------------------------------------------------------

def all_stations_activity(day):

    taken = dfAct[day]

    # Tworzenie mapy aktywności
    m_act = folium.Map(location=[52.2298, 21.0118],
                       tiles="Stamen Terrain", zoom_start=10)

    # Dodawanie markerów w zależności od aktywności stacji
    for i in range(len(dfAct)):
        # aby zapisac popup muszą być wartości typu string
        nr = str(dfAct.iloc[i]['number'])
        nazwa = str(dfAct.iloc[i]['name'])
        ilosc = str(dfAct.iloc[i][day])

        # zakresy do kolorów aktywności (pinezki)
        if taken[i] > 300:
            folium.Marker(
                location=[dfAct.iloc[i]['lat'], dfAct.iloc[i]['lng']],
                popup='stacja: ' + nr + '\n' + nazwa + '\naktywność: ' + ilosc,
                icon=folium.Icon(
                    color="red", icon="angle-double-up", prefix='fa')
            ).add_to(m_act)
        if taken[i] in range(150, 300):
            folium.Marker(
                location=[dfAct.iloc[i]['lat'], dfAct.iloc[i]['lng']],
                popup='stacja: ' + nr + '\n' + nazwa + '\naktywność: ' + ilosc,
                icon=folium.Icon(color="orange", icon="angle-up", prefix='fa')
            ).add_to(m_act)
        if taken[i] in range(50, 150):
            folium.Marker(
                location=[dfAct.iloc[i]['lat'], dfAct.iloc[i]['lng']],
                popup='stacja: ' + nr + '\n' + nazwa + '\naktywność: ' + ilosc,
                icon=folium.Icon(color="blue", icon="angle-down", prefix='fa')
            ).add_to(m_act)
        if taken[i] in range(0, 50):
            folium.Marker(
                location=[dfAct.iloc[i]['lat'], dfAct.iloc[i]['lng']],
                popup='stacja: ' + nr + '\n' + nazwa + '\naktywność: ' + ilosc,
                icon=folium.Icon(color="darkblue",
                                 icon="angle-double-down", prefix='fa')
            ).add_to(m_act)
    return m_act


# -------------------------------------------------------------------
# Graficzny interfejs użytkownika
# -------------------------------------------------------------------

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

    def initWindow(self):
        self.setWindowTitle(self.tr("Analiza rowerów"))
        self.setMinimumSize(1000, 800)
        self.showMaximized()
        self.buttonUI()
        print(self)

    def buttonUI(self):

        button1 = QtWidgets.QPushButton(self.tr("Wyznacz trasę"))
        button1.setFont(QtGui.QFont("Arial font", 13))
        button2 = QtWidgets.QPushButton(self.tr("Rozmieszczenie stacji"))
        button2.setFont(QtGui.QFont("Arial font", 13))
        button3 = QtWidgets.QPushButton(self.tr("Aktywność stacji"))
        button3.setFont(QtGui.QFont("Arial font", 13))
        button4 = QtWidgets.QPushButton(
            self.tr("Wyświetl tygodniowy wykres aktywności"))
        button4.setFont(QtGui.QFont("Arial font", 11))

        self.one_super_label = QtWidgets.QLabel()
        self.one_super_label.setFont(QtGui.QFont("Arial font", 12))
        self.title_label = QtWidgets.QLabel(
            "Wizualizacja danych\nz warszawskich rowerów\nVeturillo ")
        self.title_label.setFont(QtGui.QFont("Roboto", 20))
        self.empty_label = QtWidgets.QLabel()
        self.graphWidget = pg.PlotWidget()

        button1.setFixedSize(280, 40)
        button2.setFixedSize(280, 40)
        button3.setFixedSize(280, 40)
        button4.setFixedSize(280, 40)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(40, 50, 50, 50)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QHBoxLayout(central_widget)

        button_container = QtWidgets.QWidget()
        vlay = QtWidgets.QVBoxLayout(button_container)
        vlay.setSpacing(20)
        vlay.addWidget(self.title_label)
        vlay.addWidget(self.empty_label)
        vlay.addWidget(self.one_super_label)
        vlay.addWidget(button1)
        vlay.addWidget(button2)
        vlay.addWidget(button3)
        vlay.addWidget(button4)
        vlay.addStretch()
        lay.addWidget(button_container)
        lay.addWidget(self.view, stretch=1)

        def show_map(m):
            data = io.BytesIO()
            m.save(data, close_file=False)
            self.view.setHtml(data.getvalue().decode())

        def show_activity_station(self):
            days = ["Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"]
            days, done1 = QtWidgets.QInputDialog.getItem(
                self, 'Wybierz dzień', 'Dzień:', days)

            if done1:
                self.one_super_label.setText("Wybrano dzień: " + str(days))
                ma = all_stations_activity(str(days))
                data = io.BytesIO()
                ma.save(data, close_file=False)
                self.view.setHtml(data.getvalue().decode())

        def show_activity_station_plot(self):
            stationNames = []
            for i in range(len(stations)):
                stationNames.append(stations[i]["name"])
            stationNames, done1 = QtWidgets.QInputDialog.getItem(
                self, 'Wybierz stacje', 'Stacja:', stationNames)

            if done1:
                self.one_super_label.setText(
                    "Wybrano stacje: " + str(stationNames))
                # wywołanie funkcji, która wyświetla wykres aktywności w nowym oknie
                plot_activity(str(stationNames))

        def show_bike_road(self):
            bikes_num = []
            for i in range(len(stations)):
                tab_bikes = stations[i]["bike_numbers"].split(",")
                bikes_num.extend(tab_bikes)

            bikes_num, done1 = QtWidgets.QInputDialog.getItem(
                self, 'Wybór roweru', 'Wybierz numer roweru:', bikes_num)

            if done1:
                self.one_super_label.setText("Wybrano rower: " + bikes_num)
                m = bike_road(bikes_num)
                data = io.BytesIO()
                m.save(data, close_file=False)
                self.view.setHtml(data.getvalue().decode())
        m = show_stations()
        show_map(m)

        button1.clicked.connect(lambda: show_bike_road(self))
        button2.clicked.connect(lambda: show_map(m))
        button3.clicked.connect(lambda: show_activity_station(self))
        button4.clicked.connect(lambda: show_activity_station_plot(self))


if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())
