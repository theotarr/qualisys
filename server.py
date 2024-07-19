import zmq
import json
import asyncio
import qtm_rt

IP_ADDRESS = "140.247.112.125"
PASSWORD = "$KHU15"


def on_packet(packet):
    """Callback function that is called everytime a data packet arrives from QTM"""
    _, markers = packet.get_3d_markers()

    points = [[marker.x, marker.y, marker.z] for marker in markers]
    print(f"Received data for frame {packet.framenumber}, {len(points)} markers")

    dict_market = {"markers": points}
    marker_json = json.dumps(dict_market)

    # Publish message to all subscribers.
    publisher.send_string(marker_json)


async def setup():
    """Set up the connection to QTM and start streaming frames"""
    print(f"Attempting to connect to QTM at {IP_ADDRESS}")
    try:
        connection = await asyncio.wait_for(
            qtm_rt.connect(IP_ADDRESS, version="1.8"), timeout=5.0
        )
        if connection is None:
            print("Failed to connect to QTM")
            return None

        print("Connected to QTM")
        await connection.stream_frames(
            components=["3d"], frames="frequency:40", on_packet=on_packet
        )

        return connection
    except asyncio.TimeoutError:
        print("Connection attempt timed out")
        return None
    except Exception as e:
        print(f"Error connecting to QTM: {e}")
        return None


if __name__ == "__main__":
    # Set up the publisher.
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://*:5555")

    # Set up the asyncio event loop to continuously receive data and then publish messages.
    asyncio.ensure_future(setup())
    asyncio.get_event_loop().run_forever()
