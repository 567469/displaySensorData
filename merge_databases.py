import pandas as pd
import sqlite3

IMPORT_DATENBANK_PFAD_AUTO = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\import_folder\\car\\"
IMPORT_DATENBANK_PFAD_PHONE = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\import_folder\\phone\\"
DATENBANK_PFAD_GESAMT = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\databases\\car_and_phone_database.db"
DATABASES_PFAD = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\databases\\"
BACKUP_DATABASES_PFAD = "C:\\Users\\simon\\Documents\\backups_databases\\"

conn_car_and_phone = sqlite3.connect(DATENBANK_PFAD_GESAMT)

dfphone = pd.read_sql_query("SELECT timestamp, gnsslatitude, gnsslongitude, speed as speed_phone, accelerometer_x, accelerometer_y, accelerometer_z, gyroscope_x, gyroscope_y, gyroscope_z, gravity_x, gravity_y, gravity_z, magnetometer_x, magnetometer_y, magnetometer_z FROM sensordata", conn_car_and_phone)
dfcar = pd.read_sql_query("SELECT timestamp, Latitude as latitude_car, Longitude as longitude_car, Speed as speed_car, Consumption as consumption FROM candata", conn_car_and_phone)

dfphone['timestamp'] = pd.to_datetime(dfphone['timestamp'])
dfcar['timestamp'] = pd.to_datetime(dfcar['timestamp'])

min_timestamp = max(dfphone['timestamp'].min(), dfcar['timestamp'].min())
max_timestamp = min(dfphone['timestamp'].max(), dfcar['timestamp'].max())

dfphone_filtered = dfphone[(dfphone['timestamp'] >= min_timestamp) & (dfphone['timestamp'] <= max_timestamp)]
dfcar_filtered = dfcar[(dfcar['timestamp'] >= min_timestamp) & (dfcar['timestamp'] <= max_timestamp)]

dfphone_filtered.set_index('timestamp', inplace=True)
dfcar_filtered.set_index('timestamp', inplace=True)

df2_new_resampled = dfcar_filtered.resample('L').mean().interpolate()
df2_new_resampled = df2_new_resampled.reindex(dfphone_filtered.index, method='nearest')

result_new = pd.merge(dfphone_filtered, df2_new_resampled, left_index=True, right_index=True, how='left')
result_new.reset_index(inplace=True)

# result_new.to_sql('temp_merged_table', conn_car_and_phone, if_exists='replace', index=True, index_label='timestamp')
result_new.to_sql('merged_data', conn_car_and_phone, if_exists='replace', index=False)

conn_car_and_phone.close()

# print(result_new.head().head())
