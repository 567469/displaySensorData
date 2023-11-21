import os
import sqlite3
import tkinter
import tkinter.messagebox
from tkinter.ttk import Label

import pandas as pd
from asammdf import MDF
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from tkintermapview import TkinterMapView

from timeSelection import SelectionDialog

IMPORT_DATENBANK_PFAD_AUTO = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\import_folder\\car\\"
IMPORT_DATENBANK_PFAD_PHONE = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\import_folder\\phone\\sensordatabase.db"
DATENBANK_PFAD = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\databases\\car_and_phone_database.db"
MAP_DATENBANK_PFAD = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\offline_tiles_freising.db"
APP_NAME = "sensorDataMapViewer.py"
WIDTH = 2900
HEIGHT = 1310

MAP_WIDTH = 1300
MAP_HEIGHT = 1000

OFFSET_MINUTES=2
OFFSET_SECONDS=43
OFFSET_MILLISECONDS=648.659


class App(tkinter.Tk):

    def add_plot_to_grid(self, figure, row, column):
        canvas = FigureCanvasTkAgg(figure, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=column, sticky="nsew")
        self.canvas_dict[(row, column)] = canvas


    def create_combined_plot_lat(self):

        fig = Figure(figsize=(16, 6), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(self.sensorDataDF['timestamp'], self.sensorDataDF['gnsslatitude'], label='Sensordata')
        ax.plot(self.canDataDF['timestamp'], self.canDataDF['latitude'], label='Candata')
        return fig

        # fig = Figure(figsize=(5, 4), dpi=100)
        # ax = fig.add_subplot(111)
        #
        # ax.plot(df1['timestamp'], df1.iloc[:, 1], label='X-Werte')
        # ax.plot(df1['timestamp'], df1.iloc[:, 2], label='Y-Werte')
        # ax.plot(df1['timestamp'], df1.iloc[:, 3], label='Z-Werte')
        #
        # ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=3, fancybox=True)
        #
        # ax.axes.get_xaxis().set_ticks([])
        # ax.set_title(titel, y=-0.08)
        # return fig

    def create_combined_plot_long(self):
        fig = Figure(figsize=(16, 6), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(self.sensorDataDF['timestamp'], self.sensorDataDF['gnsslongitude'], label='Sensordata')
        ax.plot(self.canDataDF['timestamp'], self.canDataDF['longitude'], label='Candata')
        return fig

    def get_file_paths(self, root_folder):
        file_paths = []
        for folder_name, subfolders, filenames in os.walk(root_folder):
            for filename in filenames:
                if filename.endswith("MF4"):
                    file_path = os.path.join(folder_name, filename)
                    file_paths.append(file_path)
        return file_paths

    def convert_to_unix_float(self, timestamp_value):
        utc_timestamp = pd.to_datetime(timestamp_value, utc=True)
        berlin_timestamp = utc_timestamp.tz_convert('Europe/Berlin')
        unix_float_timestamp = berlin_timestamp.timestamp()

        return unix_float_timestamp

    def get_coordinates_1(self, datum_from, datum_until):
        conn = sqlite3.connect(IMPORT_DATENBANK_PFAD_PHONE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT timestamp, gnsslatitude, gnsslongitude FROM sensordata WHERE timestamp BETWEEN \"{datum_from}\" AND \"{datum_until}\" ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(rows, columns=['timestamp', 'gnsslatitude', 'gnsslongitude'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def get_coordinates_2(self, datum_from, datum_until):
        # print("Start loading car data")
        # file_paths = self.get_file_paths(IMPORT_DATENBANK_PFAD_AUTO)
        # mdf = MDF.concatenate(file_paths)
        #
        # databases = {
        #     "CAN": [("decode_with_consumption.dbc", 0)]
        # }
        #
        # mdf_scaled = mdf.extract_bus_logging(databases)
        # df_can = mdf_scaled.to_dataframe(time_as_date=True)
        # df_can.index = df_can.index.tz_convert('Europe/Berlin')
        # df_can.index = pd.to_datetime(df_can.index) - pd.Timedelta(minutes=OFFSET_MINUTES, seconds=OFFSET_SECONDS, milliseconds=OFFSET_MILLISECONDS)
        #
        # df = df_can[(df_can.index >= datum_from) & (df_can.index <= datum_until)]
        # df.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'}, inplace=True)
        # df = df.reset_index()
        # df.rename(columns={'timestamps': 'timestamp'}, inplace=True)
        # print("Ende loading car data")

        conn = sqlite3.connect(DATENBANK_PFAD)
        cursor = conn.cursor()
        cursor.execute(f"SELECT timestamp, Latitude as latitude, Longitude as longitude FROM candata WHERE timestamp BETWEEN \"{datum_from}\" AND \"{datum_until}\" ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(rows, columns=['timestamp', 'latitude', 'longitude'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def set_active_marker_1(self, value):
        row = self.sensorDataDF.iloc[int(value)]
        timestamp_value = row['timestamp']
        lat_1 = row['gnsslatitude']
        lon_1 = row['gnsslongitude']

        if (lat_1 != 0) & (lon_1 != 0):
            if self.current_marker_1 is None:
                self.current_marker_1 = self.map_widget.set_marker(lat_1, lon_1, text=str(timestamp_value))
            else:
                self.current_marker_1.set_position(lat_1, lon_1)
                self.current_marker_1.set_text(str(timestamp_value))

    def set_active_marker_2(self, value):
        row = self.canDataDF.iloc[int(value)]
        timestamp_value = row['timestamp']
        lat_2 = row['latitude']
        lon_2 = row['longitude']

        if (lat_2 != 0) & (lon_2 != 0):
            if self.current_marker_2 is None:
                self.current_marker_2 = self.map_widget.set_marker(lat_2, lon_2, text=str(timestamp_value))
            else:
                self.current_marker_2.set_position(lat_2, lon_2)
                self.current_marker_2.set_text(str(timestamp_value))

    def __init__(self, datum_from, datum_until, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.canvas_dict = {}

        self.title(APP_NAME)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.grid_columnconfigure(0)
        self.grid_columnconfigure(1)
        self.grid_rowconfigure(0)
        self.grid_rowconfigure(1)
        self.grid_rowconfigure(2)
        self.grid_rowconfigure(3)

        self.sensorDataDF = self.get_coordinates_1(datum_from, datum_until)
        self.canDataDF = self.get_coordinates_2(datum_from, datum_until)

        self.map_widget = TkinterMapView(width=MAP_WIDTH, height=MAP_HEIGHT, corner_radius=0, max_zoom=17, use_database_only=True, database_path=MAP_DATENBANK_PFAD)
        self.map_widget.grid(row=0, column=0, rowspan=2, sticky="nsew")

        self.slider_1 = tkinter.Scale(self, from_=0, to=len(self.sensorDataDF) - 1, orient="horizontal", command=self.set_active_marker_1)
        self.slider_1.grid(row=2, column=0,  columnspan=2, sticky="nsew")

        self.slider_2 = tkinter.Scale(self, from_=0, to=len(self.canDataDF) - 1, orient="horizontal", command=self.set_active_marker_2)
        self.slider_2.grid(row=3, column=0, columnspan=2, sticky="nsew")


        sensorDataDF_without_zero_1 = self.sensorDataDF[(self.sensorDataDF['gnsslatitude'] != 0) & (self.sensorDataDF['gnsslongitude'] != 0)]
        coordinates_1 = list(zip(sensorDataDF_without_zero_1['gnsslatitude'], sensorDataDF_without_zero_1['gnsslongitude']))
        path_1 = self.map_widget.set_path(coordinates_1, color="blue", width=2)

        canDataDF_without_zero_2 = self.canDataDF[(self.canDataDF['latitude'] != 0) & (self.canDataDF['longitude'] != 0)]
        coordinates_2 = list(zip(canDataDF_without_zero_2['latitude'], canDataDF_without_zero_2['longitude']))
        path = self.map_widget.set_path(coordinates_2, color="green", width=2)

        self.fig_lat = self.create_combined_plot_lat()
        self.add_plot_to_grid(self.fig_lat, 0, 1)

        self.fig_long = self.create_combined_plot_long()
        self.add_plot_to_grid(self.fig_long, 1, 1)


        mitte_latitude = sensorDataDF_without_zero_1['gnsslatitude'].mean()
        mitte_longitude = sensorDataDF_without_zero_1['gnsslongitude'].mean()

        self.map_widget.set_position(mitte_latitude, mitte_longitude)
        self.map_widget.set_zoom(17)
        self.current_marker_1 = None
        self.current_marker_2 = None

    def clear(self):
        pass
        # self.search_bar.delete(0, last=tkinter.END)
        # self.map_widget.delete(self.search_marker)

    def on_closing(self, event=0):
        self.destroy()
        exit()

    def start(self):
        self.mainloop()


def main():
    conn = sqlite3.connect(IMPORT_DATENBANK_PFAD_PHONE)
    query = "SELECT timestamp FROM sensordata"
    df = pd.read_sql_query(query, conn)
    df['timestamp_float'] = pd.to_datetime(df['timestamp']).map(pd.Timestamp.timestamp)

    x = df['timestamp_float'].values.reshape(-1, 1)
    x = StandardScaler().fit_transform(x)
    db = DBSCAN(eps=0.1, min_samples=100).fit(x)
    labels = db.labels_
    df['cluster'] = labels
    cluster_periods = df.groupby('cluster')['timestamp'].agg(['min', 'max'])
    conn.close()

    options = [row.tolist() for index, row in cluster_periods.iterrows()]

    dialog_root = tkinter.Tk()
    dialog_root.withdraw()
    dialog = SelectionDialog(dialog_root, options)
    selected_value = dialog.show()
    dialog_root.destroy()

    if selected_value:
        app = App(selected_value[0], selected_value[1])
        app.start()
    else:
        print("Keine Auswahl getroffen. Programm beendet.")


if __name__ == "__main__":
    main()
