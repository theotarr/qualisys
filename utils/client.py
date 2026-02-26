import os
import zmq
import json
import logging
import numpy as np
from datetime import datetime

# URL for the publisher socket; override with environment variable when needed.
PUBLISHER_SOCKET = os.environ.get("PUBLISHER_SOCKET", "tcp://127.0.0.1:5555")


def connect_to_publisher(logger: logging.Logger = None) -> zmq.Socket:
    """Connect to publisher socket and return subscriber socket

    Args:
        logger (logging.Logger, optional): Logger, defaults to None.
    Returns:
        zmq.Socket: subscriber socket
    """
    if logger:
        logger.info("Connecting to publisher...")
    context = zmq.Context()

    # Set up subscriber
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(PUBLISHER_SOCKET)
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

    return subscriber


def setup_client_logger() -> logging.Logger:
    """Setup logger for client"""
    # Generate logfile name
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logfile = f"./logs/{current_time}_client_marker_processing.log"

    os.makedirs(os.path.dirname(logfile), exist_ok=True)
    logging.basicConfig(
        filename=logfile, format="%(asctime)s %(message)s", filemode="w"
    )

    logger = logging.getLogger("Client logger")
    logger.setLevel(logging.DEBUG)

    return logger


def get_qrt_data(logger: logging.Logger, socket: zmq.Socket) -> tuple:
    """Get marker data from Motion Capture.

    Returns:
        tuple: (frame_number | None, marker_data, analog_data)
    """
    frame_number = None
    marker_data = []
    analog_data = []

    rt_data = read_mocap_data(logger=logger, socket=socket)
    if not rt_data:
        if logger:
            logger.warning("No mocap data received or failed to parse frame")
        return frame_number, marker_data, analog_data

    frame_number = rt_data.get("frame_number")

    for point in rt_data.get("markers", []):
        marker_data.append(np.array(point))

    return frame_number, marker_data, analog_data


def read_mocap_data(logger: logging.Logger, socket: zmq.Socket) -> dict | None:
    """Read mocap data from publisher node.

    Returns:
        dict | None: raw data from server, or None on error
    """
    rt_data = None
    try:
        message = socket.recv_string()
        try:
            rt_data = json.loads(message)
        except json.JSONDecodeError as error:
            if logger:
                logger.error(f"An error occurred while decoding JSON: {error}")
            else:
                print(f"An error occurred while decoding JSON: {error}")
            return None

    except Exception as general_error:
        if logger:
            logger.error(f"An unexpected error occurred: {general_error}")
        else:
            print(f"An unexpected error occurred: {general_error}")
        return None

    return rt_data
