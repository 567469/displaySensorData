import math
import os
import sqlite3
from datetime import datetime

from asammdf import MDF

from variables import ALL_DATABASE_PATH, ALL_FOLDER_PATH

conn_car_and_phone = sqlite3.connect(ALL_DATABASE_PATH)
cursor_car_and_phone = conn_car_and_phone.cursor()


def get_file_paths(root_folder):
    file_paths = []
    for folder_name, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith("MF4"):
                file_path = os.path.join(folder_name, filename)
                file_paths.append(file_path)
    return file_paths


# Einlesen aller Koordinaten
# --------------------------------------------------------------------
print("Start loading mdf Paths")
file_paths = get_file_paths(ALL_FOLDER_PATH)
print("End loading mdf Paths")

print("Start concat mdf Files")
mdf = MDF.concatenate(file_paths)
print("End concat mdf Files")

databases = {
    "CAN": [("decode_with_consumption.dbc", 0)]
}
print("Start Extract can data")
mdf_scaled = mdf.extract_bus_logging(databases)
print("End Extract can data")

print("Start conversion to df")
df_can = mdf_scaled.to_dataframe(time_as_date=True, use_interpolation=False)
df_can.index = df_can.index.tz_convert('Europe/Berlin')
print("End conversion to df")

# Daten Bereinigung
# ----------------------------------------------------------------------------------------------------------------------
df_can = df_can.dropna(subset=['Latitude', 'Longitude'], how='all')
df_all = df_can[['Latitude', 'Longitude']].copy()

# ----------------------------------------------------------------------------------------------------------------------
print("Start Insert to SQL")
df_all.to_sql('temp_candata', conn_car_and_phone, if_exists='replace',
              index=True, index_label='timestamp')

cursor_car_and_phone.execute(
    "UPDATE temp_candata SET timestamp = strftime('%Y-%m-%d %H:%M:%f', timestamp) || '+01:00' WHERE length(timestamp) = 25")
conn_car_and_phone.commit()

print("End Insert to SQL")
conn_car_and_phone.close()


# --------------------------------------------------------------------

# Berechnung Abstand
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(
        dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371
    return c * r


def berechne_gesamtkilometer(db_path, zeit_schwellenwert_minuten=1):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Latitude, Longitude, timestamp FROM temp_candata ORDER BY timestamp")
    positionen = cursor.fetchall()

    gesamtkilometer = 0
    for i in range(1, len(positionen)):
        lat1, lon1, zeitstempel1 = positionen[i - 1]
        lat2, lon2, zeitstempel2 = positionen[i]
        zeit1 = datetime.strptime(zeitstempel1, "%Y-%m-%d %H:%M:%S.%f%z")
        zeit2 = datetime.strptime(zeitstempel2, "%Y-%m-%d %H:%M:%S.%f%z")
        if (zeit2 - zeit1).total_seconds() > zeit_schwellenwert_minuten * 60:
            continue

        gesamtkilometer += haversine(lat1, lon1, lat2, lon2)

    conn.close()
    return gesamtkilometer


gesamtkilometer = berechne_gesamtkilometer(ALL_DATABASE_PATH)
print(f"Gesamtkilometer: {gesamtkilometer:.2f} km")
