import c3d
import zmq
import json
import time

"""This is a demo of the arm swing visualization using a sample QTM file as input."""
ORIGINAL_FPS = 200
FPS = 40


def get_packet(frame: int, markers: list):
    print(f"Received data for frame {frame}, {len(markers)} markers")
    
    markers = markers.tolist()
    
    markers = [[marker[0], marker[1], marker[2]] for marker in markers]
    marker_json = json.dumps({
        "frame_number": frame,
        "markers": markers,
    })

    publisher.send_string(marker_json)


if __name__ == "__main__":
    # Set up the publisher.
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://*:5555")

    
    # Read the C3D file.
    reader = c3d.Reader(open('data/arm_swing.c3d', 'rb'))
    frames = reader.read_frames()
    
    # Calculate the delay between frames based on the original and desired FPS.
    delay = 1 / (FPS)
    
    # Publish the frames.
    for i, points, analog in frames:
        if i % 5 != 0:
            continue
        
        get_packet(i, points)
        time.sleep(delay)  # Introduce a delay to achieve the desired frame rate.
