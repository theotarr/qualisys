import os
import json
import logging
import numpy as np
import zmq


from datetime import datetime
from utils.logging import print_elapsed_time

PUBLISHER_SOCKET = "tcp://127.0.0.1:5555"


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


def get_qrt_data(logger: logging.Logger, socket: zmq.Socket) -> dict:
    """Get marker data from Motion Capture

    Args:
        logger (logging.Logger): logger
        socket (zmq.Socket): zmq publisher socket

    Returns:
        dict: contains organized marker data
    """
    # Retrieve data from server
    marker_data = []
    analog_data = []

    rt_data = read_mocap_data(logger=logger, socket=socket)

    # Measure time to build dicts
    for point in rt_data["markers"]:
        marker_data.append(np.array(point))

    # logger.info(f"timestamp: \n{time.time()}")
    # logger.info(f"Marker data: \n{marker_data}")
    # logger.info(f"Analog data: \n{analog_data}")

    return marker_data, analog_data


def read_mocap_data(logger: logging.Logger, socket: zmq.Socket) -> dict:
    """Read mocap data from publisher node

    Args:
        logger (logging.Logger): logger
        socket (zmq.Socket): zmq socket
    Returns:
        dict: contains raw data from server
    """
    try:
        # Read data from publisher
        message = socket.recv_string()
        try:
            rt_data = json.loads(message)
        except json.JSONDecodeError as error:
            print(f"An error occurred while decoding JSON: {error}")
            return rt_data

    except Exception as general_error:
        print(f"An unexpected error occurred: {general_error}")

    return rt_data
