import sqlite3
import matplotlib

matplotlib.use('Agg')  # Menginstal backend Matplotlib untuk menyimpan file dalam memori tanpa menampilkan jendela
import matplotlib.pyplot as plt
import cartopy.crs as ccrs  # Mengimpor modul yang akan memungkinkan kita bekerja dengan proyeksi peta
import cartopy.feature as cfeature

class DB_Map():
    def __init__(self, database):
        self.database = database  # Menginisiasi jalur database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)  # Menghubungkan ke database
        with conn:
            # Membuat tabel, jika tidak ada, untuk menyimpan kota pengguna
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()  # Menyimpan perubahan

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Mencari kota dalam database berdasarkan nama
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                # Menambahkan kota ke daftar kota pengguna
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1  # Menunjukkan bahwa operasi berhasil
            else:
                return 0  # Menunjukkan bahwa kota tidak ditemukan

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Memilih semua kota pengguna
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities  # Mengembalikan daftar kota pengguna

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Mendapatkan koordinat kota berdasarkan nama
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates  # Mengembalikan koordinat kota

    def create_graph(self, path, cities):
        # Buat peta dengan menandai setiap kota dalam daftar
        fig = plt.figure(figsize=(10, 7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        ax.coastlines(resolution='110m')
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

        coordinates = []
        for city in cities:
            coord = self.get_coordinates(city)
            if coord:
                coordinates.append((city, coord[0], coord[1]))

        if not coordinates:
            raise ValueError('Tidak ada kota yang valid untuk digambar.')

        lats = [lat for _, lat, _ in coordinates]
        lngs = [lng for _, _, lng in coordinates]

        for city, lat, lng in coordinates:
            ax.plot(lng, lat, 'ro', markersize=6, transform=ccrs.Geodetic())
            ax.text(lng + 0.5, lat + 0.5, city, transform=ccrs.Geodetic(), fontsize=9,
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

        margin = 5
        min_lon = min(lngs) - margin
        max_lon = max(lngs) + margin
        min_lat = min(lats) - margin
        max_lat = max(lats) + margin
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

        plt.savefig(path, bbox_inches='tight')
        plt.close(fig)

    def draw_distance(self, city1, city2):
        # Menggambar garis antara dua kota untuk menampilkan jarak
        pass


if __name__ == "__main__":
    m = DB_Map("database.db")  # Membuat objek yang akan berinteraksi dengan database
    m.create_user_table()   # Membuat tabel dengan kota pengguna, jika tidak sudah ada