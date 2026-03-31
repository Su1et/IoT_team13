import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        # Ініціалізуємо джерело даних
        self.datasource = Datasource(user_id=1)
        # Створюємо маркер для нашої машини
        self.car_marker = MapMarker(lat=50.4501, lon=30.5234, source="images/car.png")

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        # Запускаємо функцію update кожну 1 секунду (оновлення карти)
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        # Отримуємо нові точки з нашого WebSocket
        points = self.datasource.get_new_points()
        if not points:
            return

        for point in points:
            # Згідно з datasource.py, point це tuple: (latitude, longitude, road_state)
            lat, lon, road_state = point

            # 1. Оновлюємо позицію машини
            self.update_car_marker((lat, lon))

            # 2. Перевіряємо стан дороги і ставимо відповідні маркери ям
            if road_state == "small pit" or road_state == "large pit":
                self.set_pothole_marker((lat, lon))
            elif road_state == "bump":
                self.set_bump_marker((lat, lon))

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        lat, lon = point
        self.car_marker.lat = lat
        self.car_marker.lon = lon
        # Центруємо мапу на машинці, щоб вона завжди була в фокусі
        self.mapview.center_on(lat, lon)

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """
        lat, lon = point
        # Створюємо новий маркер з іконкою ями і додаємо на карту
        marker = MapMarker(lat=lat, lon=lon, source="images/pothole.png")
        self.mapview.add_marker(marker)

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """
        lat, lon = point
        # Створюємо новий маркер з іконкою поліцейського і додаємо на карту
        marker = MapMarker(lat=lat, lon=lon, source="images/bump.png")
        self.mapview.add_marker(marker)

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        # Стартові координати (приблизно центр, вони відразу оновляться як підуть дані)
        self.mapview = MapView(zoom=15, lat=50.4501, lon=30.5234)
        
        # Додаємо маркер машини на мапу при старті
        self.mapview.add_marker(self.car_marker)
        
        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()