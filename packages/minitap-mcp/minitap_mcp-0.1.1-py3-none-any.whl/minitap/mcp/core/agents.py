import os

from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders


def get_mobile_use_agent():
    config = Builders.AgentConfig
    custom_adb_socket = os.getenv("ADB_SERVER_SOCKET")
    if custom_adb_socket:
        parts = custom_adb_socket.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid ADB server socket: {custom_adb_socket}")
        _, host, port = parts
        config = config.with_adb_server(host=host, port=int(port))
    return Agent(config=config.build())


agent = get_mobile_use_agent()
