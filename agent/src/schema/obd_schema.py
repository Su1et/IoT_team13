from marshmallow import Schema, fields

class ObdSchema(Schema):
    speed = fields.Number()
    rpm = fields.Number()