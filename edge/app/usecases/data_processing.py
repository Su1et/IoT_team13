from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    z_value = agent_data.accelerometer.z
    speed = agent_data.obd.speed
    road_state = "normal"

    if z_value < 5 or z_value > 155000:
        road_state = "large pit"
    elif z_value < 1 or z_value > 150000:
        road_state = "small pit"
    elif z_value > 18000 and z_value < 19000:
        road_state = "bump"

    severity = abs(z_value) / (speed + 1)

    return ProcessedAgentData(
        road_state=road_state,
        severity=severity,
        agent_data=agent_data
    )