from dataclasses import dataclass
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.obd import Obd

@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    obd: Obd
    timestamp: datetime