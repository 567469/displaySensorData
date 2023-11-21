import tkintermapview

top_left_position = (48.577583, 11.248364)
bottom_right_position = (48.041789, 12.248298)
zoom_min = 1
zoom_max = 17

database_path = r"C:\Users\simon\Desktop\DB.Browser.for.SQLite-3.12.2-win64\offline_tiles_freising.db"

loader = tkintermapview.OfflineLoader(path=database_path)

loader.save_offline_tiles(top_left_position, bottom_right_position, zoom_min, zoom_max)

loader.print_loaded_sections()
