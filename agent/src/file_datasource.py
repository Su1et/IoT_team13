from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        self.acc_file = accelerometer_filename
        self.gps_file = gps_filename
        self.acc_data = []
        self.gps_data = []
        self.index = 0

    def startReading(self, *args, **kwargs):
        """Читання файлів у памʼять"""
        with open(self.acc_file, 'r') as f:
            csv_reader = reader(f)
            next(csv_reader)  # skip header
            self.acc_data = [row for row in csv_reader]

        with open(self.gps_file, 'r') as f:
            csv_reader = reader(f)
            next(csv_reader)
            self.gps_data = [row for row in csv_reader]

        self.index = 0

    def read(self) -> AggregatedData:
        """Повертає один запис (циклічно)"""

        if not self.acc_data or not self.gps_data:
            raise Exception("Datasource not initialized.")

        # циклічне читання
        acc_row = self.acc_data[self.index % len(self.acc_data)]
        gps_row = self.gps_data[self.index % len(self.gps_data)]

        self.index += 1

        accelerometer = Accelerometer(
            x=int(acc_row[0]),
            y=int(acc_row[1]),
            z=int(acc_row[2])
        )

        gps = Gps(
            longitude=float(gps_row[0]),
            latitude=float(gps_row[1])
        )

        return AggregatedData(
            accelerometer=accelerometer,
            gps=gps,
            timestamp=datetime.utcnow()
        )

    def stopReading(self, *args, **kwargs):
        """Очищення"""
        self.acc_data = []
        self.gps_data = []
        self.index = 0