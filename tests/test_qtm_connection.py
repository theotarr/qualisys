"""
Connect to QTM and streams 3D data forever
"""

import asyncio
import qtm_rt

IP_ADDRESS = "140.247.112.125"
PASSWORD = "$KHU15"


def on_packet(packet):
    """Callback function that is called everytime a data packet arrives from QTM"""
    print(f"Framenumber: {packet.framenumber}")
    header, markers = packet.get_3d_markers()
    print(f"Component info: {header}")
    for marker in markers:
        print("\t", marker)


async def setup():
    """Main function"""
    connection = await qtm_rt.connect(
        IP_ADDRESS, version="1.8"
    )  # Use at least version 1.8
    if connection is None:
        return

    await connection.stream_frames(components=["3d"], on_packet=on_packet)


if __name__ == "__main__":
    asyncio.ensure_future(setup())
    asyncio.get_event_loop().run_forever()
