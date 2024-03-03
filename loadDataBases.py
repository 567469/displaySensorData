import os
import shutil
import sqlite3
import datetime

import pandas as pd
from asammdf import MDF

from gettimedifference import calculate_time_offset, plt_sth
from variables import DATENBANK_PFAD_GESAMT, IMPORT_DATENBANK_PFAD_PHONE, \
    IMPORT_DATENBANK_PFAD_AUTO, DATABASES_PFAD, BACKUP_DATABASES_PFAD


def get_file_paths(root_folder):
    file_paths = []
    for folder_name, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith("MF4"):
                file_path = os.path.join(folder_name, filename)
                file_paths.append(file_path)
    return file_paths


conn_car_and_phone = sqlite3.connect(DATENBANK_PFAD_GESAMT)
cursor_car_and_phone = conn_car_and_phone.cursor()

# Load PHONE_Data
# --------------------------------------------------------------------
print("Start loading phone data")
conn_phone = sqlite3.connect(os.path.join(IMPORT_DATENBANK_PFAD_PHONE, "sensordatabase.db"))
cursor_phone = conn_phone.cursor()

cursor_phone.execute('SELECT timestamp, gnsslatitude, gnsslongitude, speed, '
                     'accelerometer_x, accelerometer_y, accelerometer_z, '
                     'gyroscope_x, gyroscope_y, gyroscope_z, gravity_x, '
                     'gravity_y, gravity_z, magnetometer_x, magnetometer_y, '
                     'magnetometer_z, consumption_est FROM sensordata '
                     'WHERE (gnsslatitude > 0) AND (gnsslongitude > 0) ')
                     # 'AND (timestamp between \"2024-02-08 17:25:38.000000+01:00\" and \"2024-02-08 17:47:09.000000+01:00\")')

rows = cursor_phone.fetchall()
df1 = pd.DataFrame(rows, columns=['timestamp', 'gnsslatitude', 'gnsslongitude', 'speed', 'accelerometer_x',
                                  'accelerometer_y', 'accelerometer_z', 'gyroscope_x', 'gyroscope_y',
                                  'gyroscope_z', 'gravity_x', 'gravity_y', 'gravity_z', 'magnetometer_x',
                                  'magnetometer_y', 'magnetometer_z', 'consumption_est'])
df1.rename(columns={'gnsslatitude': 'latitude', 'gnsslongitude': 'longitude'}, inplace=True)
df1 = df1[['timestamp', 'latitude', 'longitude', 'speed']]

cursor_car_and_phone.executemany(
    'INSERT OR IGNORE INTO sensordata VALUES (?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
    rows)

conn_car_and_phone.commit()
conn_phone.close()
print("End loading phone data")
# --------------------------------------------------------------------

# Load CAN_Data
# --------------------------------------------------------------------
print("Start loading car data")
file_paths = get_file_paths(IMPORT_DATENBANK_PFAD_AUTO)
mdf = MDF.concatenate(file_paths)

databases = {
    "CAN": [("decode_with_consumption.dbc", 0)]
}

mdf_scaled = mdf.extract_bus_logging(databases)

# mdf_scaled.save("scaled", overwrite=True)
df_can = mdf_scaled.to_dataframe(time_as_date=True, use_interpolation=False)

# print("Start convert timestamp")
# df_can.index = pd.to_datetime(df_can.index).map(pd.Timestamp.timestamp)
# print("End convert timestamp")

df_can.index = df_can.index.tz_convert('Europe/Berlin')

# Daten Bereinigung
# ----------------------------------------------------------------------------------------------------------------------
# Loesche Datensaetze die falsche 0 Werte haben (Consumption Valid == 1)
df_can = df_can[df_can['ConsumptionValid'] != 1]
# interpoliere die Werte aus asammdf selbst, da die o.g. 0-Werte die interpolation von asammdf stoeren
df_can = df_can.interpolate(method="linear")
# Loesche verbleibende nan Werte
df_can = df_can.dropna(subset=['SpeedValid', 'Speed', 'PositionValid', 'Latitude', 'Longitude'])
# ----------------------------------------------------------------------------------------------------------------------

# Berechnete Korrektur aus gettimedifference.py
# ----------------------------------------------------------------------------------------------------------------------

plt_sth(df1, df_can)

df_can.index = pd.to_datetime(df_can.index) - pd.Timedelta(minutes=2)
plt_sth(df1, df_can)

timedelta_calc = calculate_time_offset(df1, df_can)
df_can.index = pd.to_datetime(df_can.index) - timedelta_calc
plt_sth(df1, df_can)
# ----------------------------------------------------------------------------------------------------------------------

# df_can.index = pd.to_datetime(df_can.index).map(pd.Timestamp.timestamp)
# df_can = df_can.drop(['AltitudeValid', 'Altitude', 'AltitudeAccuracy', 'FixType', 'Satellites', 'TimeValid', 'TimeConfirmed', 'Epoch', 'AltitudeValid_0', 'Altitude_0' ,'AltitudeAccuracy_0'], axis=1)

df_can.to_sql('temp_candata', conn_car_and_phone, if_exists='replace', index=True, index_label='timestamp')

cursor_car_and_phone.execute(
    "UPDATE temp_candata SET timestamp = strftime('%Y-%m-%d %H:%M:%f', timestamp) || '+01:00' WHERE length(timestamp) = 25")
conn_car_and_phone.commit()

cursor_car_and_phone.execute("INSERT OR IGNORE INTO candata SELECT * FROM temp_candata")
conn_car_and_phone.commit()

cursor_car_and_phone.execute("DROP TABLE IF EXISTS temp_candata")
conn_car_and_phone.commit()

print("End loading car data")
# --------------------------------------------------------------------

conn_car_and_phone.close()

# backup CAR_Data
# --------------------------------------------------------------------
print("Start car data backup")
for item_name in os.listdir(IMPORT_DATENBANK_PFAD_AUTO):
    source_item = os.path.join(IMPORT_DATENBANK_PFAD_AUTO, item_name)
    destination_item = os.path.join(DATABASES_PFAD, "car\\", item_name)

    if os.path.isfile(source_item):
        shutil.copy2(source_item, destination_item)
    elif os.path.isdir(source_item):
        shutil.copytree(source_item, destination_item, dirs_exist_ok=True)
print("End car data backup")
# --------------------------------------------------------------------

# backup PHONE_Data
# --------------------------------------------------------------------
print("Start phone data backup")
shutil.copy2(os.path.join(IMPORT_DATENBANK_PFAD_PHONE, "sensordatabase.db"), os.path.join(DATABASES_PFAD, "phone\\",
                                                                                          datetime.datetime.now().strftime(
                                                                                              '%y%m%d_%H%M%S') + "_" + "sensordatabase.db"))
print("End phone data backup")
# --------------------------------------------------------------------

# backup backup_folder
# --------------------------------------------------------------------
print("Start backup")
shutil.make_archive(os.path.join(BACKUP_DATABASES_PFAD, datetime.datetime.now().strftime('%y%m%d_%H%M%S')), 'zip',
                    DATABASES_PFAD)
print("End backup")
# --------------------------------------------------------------------
