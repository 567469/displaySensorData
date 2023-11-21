import sqlite3
import tkinter
import tkinter.messagebox
from tkinter.ttk import Label

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from tkintermapview import TkinterMapView

from timeSelection import SelectionDialog

DATENBANK_PFAD = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\databases\\car_and_phone_database.db"
MAP_DATENBANK_PFAD = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\offline_tiles_freising.db"
APP_NAME = "sensorDataMapViewer.py"
WIDTH = 2400
HEIGHT = 870
MAP_WIDTH = 900
MAP_HEIGHT = 800



class App(tkinter.Tk):
    def convert_to_unix_float(self, timestamp_value):
        utc_timestamp = pd.to_datetime(timestamp_value, utc=True)
        berlin_timestamp = utc_timestamp.tz_convert('Europe/Berlin')
        unix_float_timestamp = berlin_timestamp.timestamp()

        return unix_float_timestamp

    def update_plot_with_point_multiaxes(self, row, column, ax, point_x, point_y_x, point_y_y, point_y_z):
        canvas = self.canvas_dict.get((row, column))
        if canvas:
            for line in ax.lines[:]:
                if hasattr(line, 'is_point') and line.is_point:
                    line.remove()

            new_point_x, = ax.plot(point_x, point_y_x, 'ro')
            new_point_y, = ax.plot(point_x, point_y_y, 'ro')
            new_point_z, = ax.plot(point_x, point_y_z, 'ro')
            new_point_x.is_point = True
            new_point_y.is_point = True
            new_point_z.is_point = True
            canvas.draw()

    def update_plot_with_point_single(self, row, column, ax, point_x, point_y):
        canvas = self.canvas_dict.get((row, column))
        if canvas:
            for line in ax.lines[:]:
                if hasattr(line, 'is_point') and line.is_point:
                    line.remove()

            new_point_x, = ax.plot(point_x, point_y, 'ro')
            new_point_x.is_point = True
            canvas.draw()

    def create_combined_plot(self, titel, df1):
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(df1['timestamp'], df1.iloc[:, 1], label='X-Werte')
        ax.plot(df1['timestamp'], df1.iloc[:, 2], label='Y-Werte')
        ax.plot(df1['timestamp'], df1.iloc[:, 3], label='Z-Werte')

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=3, fancybox=True)

        ax.axes.get_xaxis().set_ticks([])
        ax.set_title(titel, y=-0.08)
        return fig

    def create_plot(self, titel, df1):
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(df1['timestamp'], df1.iloc[:, 1], label=titel)

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),
                  ncol=3, fancybox=True)

        ax.axes.get_xaxis().set_ticks([])
        ax.set_title(titel, y=-0.08)
        return fig

    def add_plot_to_grid(self, figure, row, column):
        canvas = FigureCanvasTkAgg(figure, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=column, sticky="nsew")
        self.canvas_dict[(row, column)] = canvas

    def get_coordinates(self, datum_from, datum_until):
        conn = sqlite3.connect(DATENBANK_PFAD)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM merged_data WHERE timestamp BETWEEN \"{datum_from}\" AND \"{datum_until}\" ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        conn.close()

        df = pd.DataFrame(rows, columns=['timestamp', 'gnsslatitude', 'gnsslongitude', 'speed_phone', 'accelerometer_x',
                                         'accelerometer_y', 'accelerometer_z', 'gyroscope_x', 'gyroscope_y',
                                         'gyroscope_z', 'gravity_x', 'gravity_y', 'gravity_z', 'magnetometer_x',
                                         'magnetometer_y', 'magnetometer_z', 'latitude_car', 'longitude_car',
                                         'speed_car', 'consumption'])

        df['speed_phone'] = df['speed_phone']*3.6
        df['speed_car'] = df['speed_car'] * 3.6
        # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True).dt.tz_convert('Europe/Berlin')
        return df

    def set_active_marker(self, value):
        row = self.sensorDataDF.iloc[int(value)]

        timestamp_value = row['timestamp']
        # timestamp_str = pd.to_datetime(timestamp_value, unit='s', utc=True).tz_convert('Europe/Berlin')
        lat_1 = row['gnsslatitude']
        lon_1 = row['gnsslongitude']

        if (lat_1 != 0) & (lon_1 != 0):
            if self.current_marker_1 is None:
                self.current_marker_1 = self.map_widget.set_marker(lat_1, lon_1, text=str(timestamp_value))
            else:
                self.current_marker_1.set_position(lat_1, lon_1)
                self.current_marker_1.set_text(str(timestamp_value))

        self.labelTime.config(text=str(timestamp_value))
        self.labelLat.config(text=f"{lat_1:.6f}")
        self.labelLong.config(text=f"{lon_1:.6f}")

        lat_2 = row['latitude_car']
        lon_2 = row['longitude_car']

        if (lat_2 != 0) & (lon_2 != 0):
            if self.current_marker_2 is None:
                self.current_marker_2 = self.map_widget.set_marker(lat_2, lon_2, text=str(timestamp_value))
            else:
                self.current_marker_2.set_position(lat_2, lon_2)
                self.current_marker_2.set_text(str(timestamp_value))

        # self.labelTime.config(text=str(timestamp_value))
        # self.labelLat.config(text=f"{lat_2:.6f}")
        # self.labelLong.config(text=f"{lon_2:.6f}")

        self.update_plot_with_point_multiaxes(0, 4, self.fig_accelerometer.get_axes()[0], timestamp_value,
                                              row['accelerometer_x'],
                                              row['accelerometer_y'], row['accelerometer_z'])
        self.update_plot_with_point_multiaxes(1, 4, self.fig_gyroscope.get_axes()[0], timestamp_value, row['gyroscope_x'],
                                              row['gyroscope_y'], row['gyroscope_z'])
        self.update_plot_with_point_multiaxes(0, 5, self.fig_gravity.get_axes()[0], timestamp_value, row['gravity_x'],
                                              row['gravity_y'], row['gravity_z'])
        self.update_plot_with_point_multiaxes(1, 5, self.fig_magnetometer.get_axes()[0], timestamp_value,
                                              row['magnetometer_x'],
                                              row['magnetometer_y'], row['magnetometer_z'])
        self.update_plot_with_point_single(0, 6, self.fig_speed_phone.get_axes()[0], timestamp_value, row['speed_phone'])
        self.update_plot_with_point_single(1, 6, self.fig_speed_car.get_axes()[0], timestamp_value, row['speed_car'])

    def __init__(self, datum_from, datum_until, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.canvas_dict = {}

        self.title(APP_NAME)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.grid_columnconfigure(0)
        self.grid_columnconfigure(1)
        self.grid_columnconfigure(2)
        self.grid_columnconfigure(3)
        self.grid_columnconfigure(4)
        self.grid_columnconfigure(5)
        self.grid_columnconfigure(6)
        self.grid_rowconfigure(0)
        self.grid_rowconfigure(1)
        self.grid_rowconfigure(2)
        self.grid_rowconfigure(3)
        self.grid_rowconfigure(4)

        self.sensorDataDF = self.get_coordinates(datum_from, datum_until)

        self.map_widget = TkinterMapView(width=MAP_WIDTH, height=MAP_HEIGHT, corner_radius=0, max_zoom=17,
                                         use_database_only=True, database_path=MAP_DATENBANK_PFAD)
        self.map_widget.grid(row=0, column=0, columnspan=4, rowspan=3, sticky="nsew")

        self.slider = tkinter.Scale(self, from_=0, to=len(self.sensorDataDF) - 1,
                                    orient="horizontal", command=self.set_active_marker)

        self.slider.grid(row=3, column=0, columnspan=7, sticky="nsew")

        self.labelTime = Label(self, text="-")
        self.labelTime.grid(row=4, column=0, sticky="w")

        self.labelLat = Label(self, text="-")
        self.labelLat.grid(row=4, column=1, sticky="w")

        self.labelLong = Label(self, text="-")
        self.labelLong.grid(row=4, column=2, sticky="w")

        df_accelerometer = self.sensorDataDF[['timestamp', 'accelerometer_x', 'accelerometer_y', 'accelerometer_z']]
        self.fig_accelerometer = self.create_combined_plot("Accelerometer", df_accelerometer)
        self.add_plot_to_grid(self.fig_accelerometer, 0, 4)

        df_gyroscope = self.sensorDataDF[['timestamp', 'gyroscope_x', 'gyroscope_y', 'gyroscope_z']]
        self.fig_gyroscope = self.create_combined_plot("Gyroscope", df_gyroscope)
        self.add_plot_to_grid(self.fig_gyroscope, 1, 4)

        df_gravity = self.sensorDataDF[['timestamp', 'gravity_x', 'gravity_y', 'gravity_z']]
        self.fig_gravity = self.create_combined_plot("Gravity", df_gravity)
        self.add_plot_to_grid(self.fig_gravity, 0, 5)

        df_magnetometer = self.sensorDataDF[['timestamp', 'magnetometer_x', 'magnetometer_y', 'magnetometer_z']]
        self.fig_magnetometer = self.create_combined_plot("Magnetometer", df_magnetometer)
        self.add_plot_to_grid(self.fig_magnetometer, 1, 5)

        df_speed_phone = self.sensorDataDF[['timestamp', 'speed_phone']]
        self.fig_speed_phone = self.create_plot("Speed Phone", df_speed_phone)
        self.add_plot_to_grid(self.fig_speed_phone, 0, 6)

        df_speed_car = self.sensorDataDF[['timestamp', 'speed_car']]
        self.fig_speed_car = self.create_plot("Speed Car", df_speed_car)
        self.add_plot_to_grid(self.fig_speed_car, 1, 6)

        sensorDataDF_without_zero_1 = self.sensorDataDF[(self.sensorDataDF['gnsslatitude'] != 0) & (self.sensorDataDF['gnsslongitude'] != 0)]
        coordinates_1 = list(zip(sensorDataDF_without_zero_1['gnsslatitude'], sensorDataDF_without_zero_1['gnsslongitude']))
        path_1 = self.map_widget.set_path(coordinates_1, color="blue", width=2)

        sensorDataDF_without_zero_2 = self.sensorDataDF[(self.sensorDataDF['latitude_car'] != 0) & (self.sensorDataDF['longitude_car'] != 0)]
        coordinates_2 = list(zip(sensorDataDF_without_zero_1['latitude_car'], sensorDataDF_without_zero_2['longitude_car']))
        path = self.map_widget.set_path(coordinates_2, color="green", width=2)


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
    conn = sqlite3.connect(DATENBANK_PFAD)
    query = "SELECT timestamp FROM sensordata"
    df = pd.read_sql_query(query, conn)
    # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True).dt.tz_convert('Europe/Berlin')
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
