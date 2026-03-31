import asyncio
import json
from datetime import datetime
import websockets
from kivy import Logger
from pydantic import BaseModel, field_validator
from config import STORE_HOST, STORE_PORT


# Pydantic models
class ProcessedAgentData(BaseModel):
    road_state: str
    user_id: int = 1 # Додано дефолтне значення, щоб не було помилок валідації
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )


class Datasource:
    def __init__(self, user_id: int):
        self.index = 0
        self.user_id = user_id
        self.connection_status = None
        self._new_points = []
        asyncio.ensure_future(self.connect_to_server())

    def get_new_points(self):
        points = self._new_points
        self._new_points = []
        return points

    async def connect_to_server(self):
        # ВИПРАВЛЕНО: Правильний шлях до WebSocket (згідно з Store API)
        uri = f"ws://{STORE_HOST}:{STORE_PORT}/ws/"
        while True:
            Logger.info(f"CONNECTING TO SERVER: {uri}")
            try:
                async with websockets.connect(uri) as websocket:
                    self.connection_status = "Connected"
                    Logger.info("SUCCESSFULLY CONNECTED TO STORE WEBSOCKET!")
                    while True:
                        data = await websocket.recv()
                        parsed_data = json.loads(data)
                        self.handle_received_data(parsed_data)
            except websockets.ConnectionClosedOK:
                self.connection_status = "Disconnected"
                Logger.info("SERVER DISCONNECT")
            except Exception as e:
                Logger.error(f"WEBSOCKET ERROR: {e}")
                await asyncio.sleep(2) # Затримка перед перепідключенням

    def handle_received_data(self, data):
        # ВИПРАВЛЕНО: data - це вже розпарсений список, не робимо json.loads(data) вдруге
        try:
            processed_agent_data_list = sorted(
                [
                    ProcessedAgentData(**processed_data_json)
                    for processed_data_json in data
                ],
                key=lambda v: v.timestamp,
            )
            new_points = [
                (
                    processed_agent_data.latitude,
                    processed_agent_data.longitude,
                    processed_agent_data.road_state,
                )
                for processed_agent_data in processed_agent_data_list
            ]
            self._new_points.extend(new_points)
            Logger.info(f"Received and processed {len(new_points)} new points!")
        except Exception as e:
            Logger.error(f"Error processing data: {e}")