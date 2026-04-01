from marshmallow import Schema, fields
from schema.accelerometer_schema import AccelerometerSchema
from schema.gps_schema import GpsSchema
from schema.obd_schema import ObdSchema

class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    obd = fields.Nested(ObdSchema)
    timestamp = fields.DateTime("iso")