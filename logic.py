import sqlite3
import matplotlib

matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import cartopy.crs as ccrs  
import cartopy.feature as cfeature

class DB_Map():
    def __init__(self, database):
        self.database = database  
        self.user_colors = {}  

    def create_user_table(self):
        conn = sqlite3.connect(self.database)  
        with conn:
            
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()  

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1  
            else:
                return 0  

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities  

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates  

    def set_user_color(self, user_id, color):
        
        self.user_colors[user_id] = color
        return True

    def get_user_color(self, user_id):
        
        return self.user_colors.get(user_id, 'red')

    def create_graph(self, path, cities, marker_color='red'):
        
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
            ax.plot(lng, lat, marker='o', color=marker_color, markersize=8, transform=ccrs.Geodetic())
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
        
        pass


if __name__ == "__main__":
    m = DB_Map("database.db") 
    m.create_user_table()   
