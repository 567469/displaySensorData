import sqlite3

import pandas as pd

from variables import DATENBANK_PFAD_GESAMT

conn_car_and_phone = sqlite3.connect(DATENBANK_PFAD_GESAMT)

datum_from = '2024-02-20 10:57:00.000000+01:00'
datum_until = '2024-02-20 11:49:00.000000+01:00'

dfphone = pd.read_sql_query(
    'SELECT timestamp, gnsslatitude, gnsslongitude, speed as speed_phone, '
    'accelerometer_x, accelerometer_y, accelerometer_z, gyroscope_x, '
    'gyroscope_y, gyroscope_z, gravity_x, gravity_y, gravity_z, magnetometer_x, '
    'magnetometer_y, magnetometer_z, consumption_est '
    f'FROM sensordata WHERE timestamp BETWEEN \"{datum_from}\" AND \"{datum_until}\"',
    conn_car_and_phone)
dfcar = pd.read_sql_query(
    'SELECT timestamp, Latitude as latitude_car, Longitude as longitude_car, '
    'Speed as speed_car, Consumption as consumption FROM candata '
    f'WHERE timestamp BETWEEN \"{datum_from}\" AND \"{datum_until}\"',
    conn_car_and_phone)

dfphone['timestamp'] = pd.to_datetime(dfphone['timestamp'])
dfcar['timestamp'] = pd.to_datetime(dfcar['timestamp'])

min_timestamp = max(dfphone['timestamp'].min(), dfcar['timestamp'].min())
max_timestamp = min(dfphone['timestamp'].max(), dfcar['timestamp'].max())

dfphone_filtered = dfphone[
    (dfphone['timestamp'] >= min_timestamp) & (
            dfphone['timestamp'] <= max_timestamp)]
dfcar_filtered = dfcar[
    (dfcar['timestamp'] >= min_timestamp) & (
            dfcar['timestamp'] <= max_timestamp)]

dfphone_filtered.set_index('timestamp', inplace=True)
dfcar_filtered.set_index('timestamp', inplace=True)

df2_new_resampled = dfcar_filtered.resample('100L').mean()  # .interpolate()
df2_new_resampled = df2_new_resampled.reindex(dfphone_filtered.index,
                                              method='nearest')

result_new = pd.merge(dfphone_filtered, df2_new_resampled, left_index=True,
                      right_index=True, how='left')
result_new.reset_index(inplace=True)

result_new.to_sql('merged_data', conn_car_and_phone, if_exists='append',
                  index=False)

conn_car_and_phone.close()
