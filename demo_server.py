"""Replay a sample C3D file as a fake real-time Qualisys marker stream."""

import json
import os
import time

import c3d
import zmq

FPS = int(os.environ.get("DEMO_FPS", "40"))
FRAME_STEP = int(os.environ.get("DEMO_FRAME_STEP", "5"))
PUBLISH_BIND = os.environ.get("PUBLISH_BIND", "tcp://*:5555")
C3D_PATH = os.environ.get("DEMO_C3D_PATH", "data/arm_swing.c3d")


def publish_packet(frame: int, markers: list):
    print(f"Replay frame {frame} ({len(markers)} markers)")

    markers = markers.tolist()
    markers = [[marker[0], marker[1], marker[2]] for marker in markers]
    marker_json = json.dumps({"frame_number": frame, "markers": markers})
    publisher.send_string(marker_json)


if __name__ == "__main__":
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind(PUBLISH_BIND)
    print(f"Publishing demo marker stream on {PUBLISH_BIND}")

    with open(C3D_PATH, "rb") as c3d_file:
        reader = c3d.Reader(c3d_file)
        frames = reader.read_frames()

        delay = 1 / FPS
        for i, points, _ in frames:
            if i % FRAME_STEP != 0:
                continue

            publish_packet(i, points)
            time.sleep(delay)
