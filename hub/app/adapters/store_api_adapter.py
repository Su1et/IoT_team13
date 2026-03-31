import logging
from typing import List
import requests

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]) -> bool:
        try:
            url = f"{self.api_base_url}/processed_agent_data/"

            payload = [item.model_dump(mode="json") for item in processed_agent_data_batch]

            response = requests.post(url, json=payload)

            if response.status_code == 200:
                logging.info("Batch successfully sent to Store API")
                return True
            else:
                logging.error(f"Failed to send data: {response.text}")
                return False

        except Exception as e:
            logging.error(f"Error sending data to Store API: {e}")
            return False