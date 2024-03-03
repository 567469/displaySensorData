# Pakete laden
library(DBI)
library(ggplot2)
library(lubridate)
library(dplyr)

# Angeben des Ordnernamens
ordnername <- "C:/.../CAN_LOG_VIDEO"
startTimeStamp<- "2023-09-30 00:13:08"

pfad_erste_datei <- file.path(ordnername, "XXX_dec.csv")
pfad_zweite_datei <- file.path(ordnername, "daten.csv")

data1 <- read.csv(pfad_erste_datei, header=TRUE, sep=";", stringsAsFactors=FALSE)
data2 <- read.csv(pfad_zweite_datei, header=TRUE, sep=",", stringsAsFactors=FALSE)


# Konvertieren der 'Time' Spalte aus zweite_datei in eine Zeitdifferenz
zeit_parts <- strsplit(data2$Time, ":")
zeit_in_sekunden <- sapply(zeit_parts, function(parts) {
  min <- as.numeric(parts[1])
  sek <- as.numeric(parts[2])
  ms <- as.numeric(parts[3]) / 1000
  return(min*60 + sek + ms)
})

start_datum_zeit <- as.POSIXct(startTimeStamp, format="%Y-%m-%d %H:%M:%S", tz="UTC")
start_milliseconds <- 123 / 1000
start_datum_zeit <- start_datum_zeit + start_milliseconds

data2$Time <- start_datum_zeit + zeit_in_sekunden

data1$Time <- as.POSIXct(data1$Time, format="%Y-%m-%d %H:%M:%OS", tz="UTC")
data2$Time <- as.POSIXct(data2$Time, format="%Y-%m-%d %H:%M:%OS3", tz="UTC")


# Konvertiere timestamp zu POSIXct für beide Daten
data1$Time <- ymd_hms(data1$Time, truncated = 6)
data2$Time <- ymd_hms(data2$Time, truncated = 6)

data1$DataByte_2 <- data1$DataByte_2 / 2.5
data1 <- filter(data1, data1$DataByte_1 != 1)
data1_red <- subset(data1, select = c(Time, DataByte_2))



#data2$timestamp <- data2$timestamp - minutes(2) - seconds(43)

# Erstelle einen gemeinsamen Dataframe für ggplot
combined_data <- rbind(data1_red, data2)
combined_data$table <- factor(c(rep("Table1", nrow(data1_red)), rep("Table2", nrow(data2))))

#start_date <- as.POSIXct("2023-09-30 00:35:00", format="%Y-%m-%d %H:%M:%OS", tz="UTC")
#end_date <- as.POSIXct("2023-09-30 00:42:00", format="%Y-%m-%d %H:%M:%OS", tz="UTC")

#combined_data <- filter(combined_data, Time >= start_date & Time <= end_date)

# Plot für Longitude
p2 <- ggplot(combined_data, aes(x = Time, y = DataByte_2, color = table)) +
  geom_line() +
  labs(title = "Longitude over Time", x = "Timestamp", y = "DataByte_2")

# Zeige die Plots an
#print(p1)
print(p2)

mittelwert_data1 <- mean(data1$DataByte_2, na.rm = TRUE)

print(mittelwert_data1)