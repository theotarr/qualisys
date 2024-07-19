import zmq
import time
import json
import asyncio
import qtm_rt
import numpy as np
from utils.logging import print_elapsed_time

IP_ADDRESS = "140.247.112.125"
PASSWORD = "$KHU15"


# @print_elapsed_time()
def on_packet(packet):
    """Callback function that is called everytime a data packet arrives from QTM"""
    _, markers = packet.get_3d_markers()

    points = [[marker.x, marker.y, marker.z] for marker in markers]
    print(f"Received data for frame {packet.framenumber}, {len(points)} markers")

    dict_market = {"markers": points}

    marker_json = json.dumps(dict_market)

    # Publish message to all subscribers
    publisher.send_string(marker_json)


async def setup():
    print(f"Attempting to connect to QTM at {IP_ADDRESS}")
    try:
        connection = await asyncio.wait_for(
            qtm_rt.connect(IP_ADDRESS, version="1.8"), timeout=5.0
        )
        if connection is None:
            print("Failed to connect to QTM")
            return None

        print("Connected to QTM")
        await connection.stream_frames(components=["3d"], frames="frequency:30", on_packet=on_packet)
        
        return connection
    except asyncio.TimeoutError:
        print("Connection attempt timed out")
        return None
    except Exception as e:
        print(f"Error connecting to QTM: {e}")
        return None
    



if __name__ == "__main__":
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://*:5555")

    asyncio.ensure_future(setup())
    asyncio.get_event_loop().run_forever()
    
    
    # # This is a test to see if the pub/sub model works
    # iteration = 0
    
    # while True:
    #     time.sleep(0.05)
        
    #     print(iteration)
    #     iteration += 1
    #     publisher.send_string(json.dumps({
    #         'markers': [0, 1, 2, 3, 4, 5]
    #     }))
