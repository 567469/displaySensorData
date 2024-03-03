Dieses Repository ist Teil der Bachelorarbeit von Simon J. Heilmeier (Matr.Nr.: 567469) mit dem Titel:

# Prototypische Entwicklung einer Smartphone-Anwendung zur Verbrauchserkennung elektrifizierter Fahrzeuge

Bei der Implementierung der fogenden Scripte wurde ChatGPT4 [^1] verwendet um im Entwicklungsprozess zu unterstützen.

Inhaltsverzeichnis:

- [Anfangskorellation_Zeit.R](https://github.com/567469/graphs_obd/blob/master/Anfangskorellation_Zeit.R)  --> R-Script zur Berechnung der Zeitverschiebung zwischen den CAN-Daten und den sensordaten
- [Eliminate_XXX_Zero.R](https://github.com/567469/displaySensorData/blob/master/Eliminate_XXX_Zero.R)  --> R-Script zur Darstellung der verfälschung durch die Null-Bloecke
- [Vergleich_Merged_Video.R](https://github.com/567469/displaySensorData/blob/master/Vergleich_Merged_Video.R)  --> R-Script zur Darstellung der Video-CSV-Daten gegenübergestellt mit den zusammengeführten CAN- und Sensordaten
- [comparison_can_phone.py](https://github.com/567469/displaySensorData/blob/master/comparison_can_phone.py)  --> Hilfsartefakt zum Vergleich der CAN- und Smartphone-Daten vor dem Merge  
- [comparison_merged.py](https://github.com/567469/displaySensorData/blob/master/comparison_merged.py)     --> Hilfsartefakt zum Vergleich der CAN- und Smartphone-Daten nach dem Merge
- [gesamtkilometer.py](https://github.com/567469/displaySensorData/blob/master/gesamtkilometer.py)       --> Hilfsartefakt zur Berechung der insgesamt gefahrenen Kilometer
- [gettimedifference.py](https://github.com/567469/displaySensorData/blob/master/gettimedifference.py)     --> ausgelagerte Funktionen zur Berechung der zeitlichen Verschiebung zwischen den CAN- und den Sensor-Daten
- [loadDataBases.py](https://github.com/567469/displaySensorData/blob/master/loadDataBases.py)         --> Script zum Laden und Sichern der sensordatabase.db und der CAN-Daten (.MF4)
- [merge_databases.py](https://github.com/567469/displaySensorData/blob/master/merge_databases.py)       --> Script zum zusammenführen und zeitlichen korrigieren der CAN- und den Sensor-Daten
- [timeSelection.py](https://github.com/567469/displaySensorData/blob/master/timeSelection.py)         --> ausgelagerte Funktionen zur Auswahl von zeitlichen Fahrt-Clustern (*Für die zwei Hilfsartefakte*)

Zur Ausführung benötigte Files: (*Können für die Begutachtung freigegeben werden* [Simon J. Heilmeier](mailto:567469@fom-net.de?subject=[GitHub]%20Daten-Freigabe))

- decode_with_consumption.dbc --> Datenbank zur Decodierung der CAN-Daten
  - (*enthält proprietäre Daten, die nicht für die Veröffentlichung bestimmt sind*)
- car_and_phone_database.db   --> SQLite Datenbank mit den Tabellen candata, sensordata und merged_data
  - (*enthält private Fahrt-Daten, die nicht für die Veröffentlichung bestimmt sind*)


[^1]: https://chat.openai.com/
