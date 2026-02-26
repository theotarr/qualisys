import asyncio
import json
import os

import qtm_rt
import zmq

IP_ADDRESS = os.environ.get("QTM_IP", "127.0.0.1")
QTM_VERSION = os.environ.get("QTM_RT_VERSION", "1.8")
STREAM_FREQUENCY = int(os.environ.get("STREAM_FREQUENCY", "40"))
PUBLISH_BIND = os.environ.get("PUBLISH_BIND", "tcp://*:5555")


def on_packet(packet):
    """Publish each frame from QTM over ZeroMQ."""
    _, markers = packet.get_3d_markers()
    points = [[marker.x, marker.y, marker.z] for marker in markers]
    print(f"Received frame {packet.framenumber} ({len(points)} markers)")

    marker_json = json.dumps({"frame_number": packet.framenumber, "markers": points})
    publisher.send_string(marker_json)


async def setup():
    """Connect to QTM and start streaming 3D marker frames."""
    print(f"Attempting to connect to QTM at {IP_ADDRESS} (RT v{QTM_VERSION})")
    try:
        connection = await asyncio.wait_for(
            qtm_rt.connect(IP_ADDRESS, version=QTM_VERSION), timeout=5.0
        )
        if connection is None:
            print("Failed to connect to QTM")
            return None

        print(f"Connected to QTM. Streaming 3D markers at {STREAM_FREQUENCY}Hz")
        await connection.stream_frames(
            components=["3d"],
            frames=f"frequency:{STREAM_FREQUENCY}",
            on_packet=on_packet,
        )
        return connection
    except asyncio.TimeoutError:
        print("Connection attempt timed out")
        return None
    except Exception as error:
        print(f"Error connecting to QTM: {error}")
        return None


if __name__ == "__main__":
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind(PUBLISH_BIND)
    print(f"Publishing marker stream on {PUBLISH_BIND}")

    try:
        asyncio.ensure_future(setup())
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
