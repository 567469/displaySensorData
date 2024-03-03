# Pakete laden
library(DBI)
library(ggplot2)
library(lubridate)

# Verbindung zur SQLite-Datenbank herstellen
con <- dbConnect(RSQLite::SQLite(), "C:/.../displaySensorData/databases/car_and_phone_database.db")

# Daten aus den Tabellen lesen
#data1 <- dbGetQuery(con, "SELECT timestamp, gnsslatitude as Latitude, gnsslongitude as Longitude FROM sensordata WHERE timestamp BETWEEN '2023-11-11 08:55:00' AND '2023-11-11 09:00:00'")
#data2 <- dbGetQuery(con, "SELECT timestamp, latitude, longitude FROM candata WHERE timestamp BETWEEN '2023-11-11 08:57:43' AND '2023-11-11 09:02:43'")

data1 <- dbGetQuery(con, "SELECT timestamp, gnsslatitude as Latitude, gnsslongitude as Longitude FROM sensordata WHERE timestamp BETWEEN '2023-11-11 08:55:00' AND '2023-11-11 09:00:00'")
data2 <- dbGetQuery(con, "SELECT timestamp, latitude, longitude FROM candata WHERE timestamp BETWEEN '2023-11-11 08:55:00' AND '2023-11-11 09:00:00'")

# Schließe die Datenbankverbindung
dbDisconnect(con)

# Konvertiere timestamp zu POSIXct für beide Daten
data1$timestamp <- ymd_hms(data1$timestamp, truncated = 6)
data2$timestamp <- ymd_hms(data2$timestamp, truncated = 6)

data2$timestamp <- data2$timestamp - minutes(2) - seconds(43)

# Erstelle einen gemeinsamen Dataframe für ggplot
combined_data <- rbind(data1, data2)
combined_data$table <- factor(c(rep("Table1", nrow(data1)), rep("Table2", nrow(data2))))

# Erstelle zwei separate Plots
# Plot für Latitude
p1 <- ggplot(combined_data, aes(x = timestamp, y = Latitude, color = table)) +
  geom_line() +
  labs(title = "Latitude over Time", x = "Timestamp", y = "Latitude")

# Plot für Longitude
p2 <- ggplot(combined_data, aes(x = timestamp, y = Longitude, color = table)) +
  geom_line() +
  labs(title = "Longitude over Time", x = "Timestamp", y = "Longitude")

# Zeige die Plots an
#print(p1)
print(p2)
