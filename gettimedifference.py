import pandas as pd
from matplotlib import pyplot as plt

# DATENBANK_PFAD = "C:\\Users\\simon\\PycharmProjects\\displaySensorData\\databases\\car_and_phone_database.db"

def plt_sth(df1_i, df2_i):
    df1 = df1_i.copy()
    df2 = df2_i.copy()

    df1['timestamp'] = pd.to_datetime(df1['timestamp'])
    df1.set_index('timestamp', inplace=True)

    plt.figure(figsize=(16, 9))
    plt.subplot(1, 2, 1)
    plt.plot(df1.index, df1["latitude"], label="df1_" + "latitude")
    plt.plot(df2.index, df2["Latitude"], label="df2_" + "latitude")
    plt.title('latitude')

    plt.subplot(1, 2, 2)
    plt.plot(df1.index, df1["longitude"], label="df1_" + "longitude")
    plt.plot(df2.index, df2["Longitude"], label="df2_" + "longitude")
    plt.title('longitude')

    plt.show()

def calculate_correlation(df1, df2, offset, starttime, endtime):
    df2_shifted = df2.copy()

    # set offset
    # --------------------------------------------------------------------
    df2_shifted['Longitude'] = df2_shifted['Longitude'].shift(offset * -1)
    df2_shifted['Latitude'] = df2_shifted['Latitude'].shift(offset * -1)
    # --------------------------------------------------------------------

    # calc time diff
    # --------------------------------------------------
    timestamp2 = df2_shifted.iloc[-1].name
    last_index = -1 * (offset)
    timestamp1 = df2_shifted.iloc[last_index].name
    time_diff = timestamp2 - timestamp1
    # --------------------------------------------------

    # set time frame for correlation calculation
    df2_shifted = df2_shifted[(df2_shifted.index >= starttime) & (df2_shifted.index <= endtime)]

    # correlation calculation
    # ----------------------------------------------------------------
    correlation_lat = df1['latitude'].corr(df2_shifted['Latitude'])
    correlation_long = df1['longitude'].corr(df2_shifted['Longitude'])
    return (correlation_lat + correlation_long) / 2, time_diff
    # ----------------------------------------------------------------


    # conn = sqlite3.connect(DATENBANK_PFAD)
    # cursor = conn.cursor()
    #
    # #  {2023-11-15 22:14:37.649908+01:00} {2023-11-15 22:36:46.934367+01:00}
    # date_from = datetime.strptime("2023-11-15 22:14", "%Y-%m-%d %H:%M")
    # date_until = datetime.strptime("2023-11-15 22:36", "%Y-%m-%d %H:%M")
    # date_from_can = date_from
    # date_until_can = date_until + pd.Timedelta(minutes=3)
    #
    # cursor.execute(
    #     f'SELECT timestamp, gnsslatitude as latitude, gnsslongitude as longitude FROM sensordata WHERE timestamp BETWEEN "{date_from}" AND "{date_until}"')
    # rows = cursor.fetchall()
    # df1 = pd.DataFrame(rows, columns=['timestamp', 'latitude', 'longitude'])
    #
    # # load candata
    # cursor.execute(
    #     f'SELECT timestamp, latitude, longitude FROM candata WHERE timestamp BETWEEN "{date_from_can}" AND "{date_until_can}"')
    # rows = cursor.fetchall()
    # df2 = pd.DataFrame(rows, columns=['timestamp', 'latitude', 'longitude'])
    #
    # conn.close()

def calculate_time_offset(df1_i, df2_i):
    df1 = df1_i.copy()
    df2 = df2_i.copy()

    df1['timestamp'] = pd.to_datetime(df1['timestamp'])
    df2.index = pd.to_datetime(df2.index)  # - pd.Timedelta(minutes=2, seconds=43) # , milliseconds=648.659)

    df1.set_index('timestamp', inplace=True)
    # df2.set_index('timestamp', inplace=True)

    df1.index = df1.index.tz_convert('UTC')
    df2.index = df2.index.tz_convert('UTC')

    df2_new_resampled = df2.resample('L').mean().interpolate()
    df2_new_resampled = df2_new_resampled.reindex(df1.index, method='nearest')

    # select common periode
    # -------------------------------------------------------------------------------
    start_time = max(df1.index.min(), df1.index.min())
    end_time = min(df2_new_resampled.index.max(), df2_new_resampled.index.max())
    # -------------------------------------------------------------------------------

    df1 = df1[(df1.index >= start_time) & (df1.index <= end_time)]

    max_correlation = -1
    optimal_offset = 0
    # plt_sth(df1, df2_new_resampled)
    diff = pd.Timedelta(0)

    for offset in range(1, 1000, 1):
        correlation, diff = calculate_correlation(df1, df2_new_resampled, offset, start_time, end_time)

        print(offset)
        if correlation > max_correlation:
            max_correlation = correlation
            optimal_offset = offset
        else:
            break

    print(diff)
    print(optimal_offset)
    print(max_correlation)

    return diff
    # df2_new_resampled.index = pd.to_datetime(df2_new_resampled.index) - diff
    # plt_sth(df1, df2_new_resampled)
