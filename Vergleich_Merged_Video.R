library(DBI)
library(ggplot2)
library(lubridate)
library(dplyr)

startTimeStamp<- "2023-12-20 19:53:00"

con <- dbConnect(RSQLite::SQLite(), "C:/.../displaySensorData/databases/car_and_phone_database.db")
merged_data <- dbGetQuery(con, "SELECT timestamp, Consumption FROM merged_data WHERE timestamp BETWEEN '2023-12-20 19:53:00' AND '2023-12-20 20:26:00'")
dbDisconnect(con)

video_data  <- read.csv("C:/.../CAN_LOG_VIDEO/daten.csv", header=TRUE, sep=",", stringsAsFactors=FALSE)

zeit_parts <- strsplit(video_data$timestamp, ":")
zeit_in_sekunden <- sapply(zeit_parts, function(parts) {
  min <- as.numeric(parts[1])
  sek <- as.numeric(parts[2])
  ms <- as.numeric(parts[3]) / 1000
  return(min*60 + sek + ms)
})

start_datum_zeit <- as.POSIXct(startTimeStamp, format="%Y-%m-%d %H:%M:%S", tz="UTC")
start_milliseconds <- 123 / 1000
start_datum_zeit <- start_datum_zeit + start_milliseconds

video_data$timestamp <- start_datum_zeit + zeit_in_sekunden

merged_data$timestamp <- as.POSIXct(merged_data$timestamp, format="%Y-%m-%d %H:%M:%OS", tz="UTC")
video_data$timestamp <- as.POSIXct(video_data$timestamp, format="%Y-%m-%d %H:%M:%OS3", tz="UTC")

video_data$timestamp <- video_data$timestamp - minutes(2) - seconds(18)

start_date <- as.POSIXct("2023-12-20 19:53:00", format="%Y-%m-%d %H:%M:%OS", tz="UTC")
end_date <- as.POSIXct("2023-12-20 20:26:00", format="%Y-%m-%d %H:%M:%OS", tz="UTC")
merged_data <- filter(merged_data, timestamp >= start_date & timestamp<= end_date)
video_data <- filter(video_data, timestamp >= start_date & timestamp<= end_date)

# Erstelle einen gemeinsamen Dataframe für ggplot
combined_data <- rbind(merged_data, video_data)
combined_data$table <- factor(c(rep("merged_data", nrow(merged_data)), rep("video_data", nrow(video_data))))

# Erstelle zwei separate Plots
# Plot für Latitude
#p1 <- ggplot(combined_data, aes(x = timestamp, y = consumption, color = table)) +
#  geom_line() +
#  labs(y = "Consumption")

#print(p1)

# Darstellung als Linien-Graph
gg <- ggplot(combined_data, aes(x = timestamp, y = consumption, group=table)) + 
  geom_line(aes(linetype = table, color = table, size = table)) +
  labs(x="Zeit", y="kWh/100 km") +
  theme_minimal() +
  theme(
    legend.position = "top",
    legend.title = element_text(size=14),       # Größe des Legendentitels
    legend.text = element_text(size=12),        # Größe des Legendentextes
    axis.title = element_text(size=14),         # Größe der Achsentitel
    axis.text.x = element_text(size=10),        # Größe des Textes der x-Achse
    axis.text.y = element_text(size=10)         # Größe des Textes der y-Achse
  ) +
  scale_color_manual(values=c("#E69F00", "#56B4E9"), 
                     name="Quelle", 
                     labels=c("fusioniert Daten", "Aufnahme-Daten")) +
  scale_linetype_manual(values=c("solid", "dashed"), 
                        name="Quelle", 
                        labels=c("fusioniert Daten", "Aufnahme-Daten")) +
  scale_size_manual(values=c(1.01, 0.75),                        
                    name="Quelle", 
                    labels=c("fusioniert Daten", "Aufnahme-Daten"))

print(gg)
