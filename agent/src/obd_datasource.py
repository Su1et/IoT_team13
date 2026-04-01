from csv import reader
from datetime import datetime
import random
import obd

from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.obd import Obd
from domain.aggregated_data import AggregatedData
import config


class ObdEmulator:
    def __init__(self):
        pass

    def is_connected(self):
        return True

    def query(self, command):
        class Response:
            def __init__(self, val):
                self.value = type('obj', (object,), {'magnitude': val})

            def is_null(self):
                return False

        if command == obd.commands.SPEED:
            return Response(random.uniform(40.0, 60.0))
        elif command == obd.commands.RPM:
            return Response(random.uniform(1500.0, 2500.0))
        return Response(0.0)

    def close(self):
        pass


class EnhancedDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        self.acc_file = accelerometer_filename
        self.gps_file = gps_filename
        self.acc_data = []
        self.gps_data = []
        self.index = 0

        self.connection = obd.OBD()
        if not self.connection.is_connected():
            self.connection = ObdEmulator()

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

        acc_row = self.acc_data[self.index % len(self.acc_data)]
        gps_row = self.gps_data[self.index % len(self.gps_data)]

        self.index += 1

        accelerometer = Accelerometer(
            x=int(acc_row[0]),
            y=int(acc_row[1]),
            z=int(acc_row[2])
        )

        gps = Gps(
            longitude=float(gps_row[1]),
            latitude=float(gps_row[0])
        )

        speed_cmd = self.connection.query(obd.commands.SPEED)
        rpm_cmd = self.connection.query(obd.commands.RPM)

        speed_val = speed_cmd.value.magnitude if not speed_cmd.is_null() else 0.0
        rpm_val = rpm_cmd.value.magnitude if not rpm_cmd.is_null() else 0.0

        if abs(accelerometer.z) > 16000 and isinstance(self.connection, ObdEmulator):
            speed_val = random.uniform(10.0, 20.0)
            rpm_val = speed_val * 40.0

        obd_data = Obd(
            speed=float(speed_val),
            rpm=float(rpm_val)
        )

        return AggregatedData(
            accelerometer=accelerometer,
            gps=gps,
            obd=obd_data,
            timestamp=datetime.utcnow()
        )

    def stopReading(self, *args, **kwargs):
        """Очищення"""
        self.acc_data = []
        self.gps_data = []
        self.index = 0
        self.connection.close()