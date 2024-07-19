import json
import time
import numpy as np
import matplotlib.pyplot as plt
from labels import (
    RIGHT_COM_LABELS,
    LEFT_COM_LABELS,
    RIGHT_SHOULDER_LABELS,
    LEFT_SHOULDER_LABELS,
)
from time import sleep
from client import (
    setup_client_logger,
    get_qrt_data,
    connect_to_publisher,
)
from blit import BlitManager


DESIRED_ANGLE = 160
FRAMES_PER_SECOND = 30
PAUSE_BETWEEN_FRAMES = 1 / FRAMES_PER_SECOND

left_arm_length = None
right_arm_length = None
arm_length = None
left_offset = None
right_offset = None
swing_amplitude = None


def calc_desired_arm_vector(is_front, sep_constant, arm_offset):
    y = swing_amplitude if is_front else -swing_amplitude
    desired_vector = np.array(
        [
            sep_constant + arm_offset,
            y,
            # np.cos(np.radians(angle)) * arm_length,
        ]
    )
    return desired_vector


def plot_2d_arm(
    shoulder, com, arm: str, com_point, forward_com_point, backward_com_point
):
    print(left_offset, right_offset)
    sep_constant = 100 if arm == 'right' else -100
    arm_constant = right_offset if arm == 'right' else left_offset
    
    com[0] = com[0] - shoulder[0] + sep_constant
    com[1] = com[1] - shoulder[1]
    com_point.set_data([com[0]], [com[1]])
    
    

    forward_com = calc_desired_arm_vector(True, sep_constant, arm_constant)
    backward_com = calc_desired_arm_vector(False, sep_constant, arm_constant)

    # Update the forward and backward com points
    forward_com_point.set_data([forward_com[0]], [forward_com[1]])
    backward_com_point.set_data([backward_com[0]], [backward_com[1]])


def load_com_calibration():
    # Check if `calibration.json` exists
    try:
        with open("calibration.json", "r") as f:
            # Replace None variables with the values from the file
            data = json.load(f)
            
            global left_arm_length 
            left_arm_length = data['left_arm_length']
            global right_arm_length 
            right_arm_length = data['right_arm_length']
            global arm_length 
            arm_length = data['arm_length']
            global left_offset 
            left_offset = data['left_offset']
            global right_offset 
            right_offset = data['right_offset']

    except FileNotFoundError:
        print("No COM calibration file found")
        return None, None


def main():
    # Load calibration and initialize variables
    load_com_calibration()
    global swing_amplitude
    swing_amplitude = np.sin(np.radians(DESIRED_ANGLE)) * arm_length
    
    client_logger = setup_client_logger()
    socket = connect_to_publisher(logger=client_logger)

    fig, ax = plt.subplots(figsize=(8, 8))

    # Set up the plot
    ax.set_xlim(-250, 250)
    ax.set_ylim(-250, 250)
    ax.set_aspect("equal")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(f"2D Arm Swing Visualization - Angle: {DESIRED_ANGLE}°")

    # Add the frame number
    fr_number = ax.annotate(
        "0",
        (0, 1),
        xycoords="axes fraction",
        xytext=(10, -10),
        textcoords="offset points",
        ha="left",
        va="top",
        animated=True,
    )

    # Add the COMs and target COMs
    (left_com_point,) = ax.plot(0, 0, "bo", markersize=20, animated=True)
    (left_forward_com_point,) = ax.plot(
        0, 0, "bo", markersize=40, alpha=0.7, animated=True, markerfacecolor='none', markeredgecolor='b'
    )
    (left_backward_com_point,) = ax.plot(
        0, 0, "bo", markersize=40, alpha=0.7, animated=True, markerfacecolor='none', markeredgecolor='b'
    )

    (right_com_point,) = ax.plot(0, 0, "ro", markersize=20, animated=True)
    (right_forward_com_point,) = ax.plot(
        0, 0, "ro",markerfacecolor='none', markeredgecolor='r', markersize=40, alpha=0.7, animated=True
    )
    (right_backward_com_point,) = ax.plot(
        0, 0, "ro",markerfacecolor='none', markeredgecolor='r', markersize=40, alpha=0.7, animated=True
    )

    print("Starting animation...")

    bm = BlitManager(
        fig.canvas,
        [
            fr_number,
            left_com_point,
            right_com_point,
            left_forward_com_point,
            right_forward_com_point,
            left_backward_com_point,
            right_backward_com_point,
        ],
    )
    plt.ion()  # Turn on interactive mode
    plt.show(block=False)

    plt.pause(
        0.1
    )  # Pause for some time to ensure that at least 1 frame is displayed and cached for future renders.

    packet_number = 0

    try:
        while True:
            # plt.pause(PAUSE_BETWEEN_FRAMES)
            markers, _ = get_qrt_data(logger=client_logger, socket=socket)
            print(f"Received frame {packet_number}, {len(markers)} markers")
            packet_number += 1

            # # Fill markers with random numbers if NAN
            # for i, marker in enumerate(markers):
            #     markers[i] = [np.random.randint(800, 2000), np.random.randint(800, 2000), np.random.randint(800, 2000)]

            right_shoulder_points = [markers[i][:3] for i in RIGHT_SHOULDER_LABELS]
            right_com_points = [markers[i][:3] for i in RIGHT_COM_LABELS]
            left_shoulder_points = [markers[i][:3] for i in LEFT_SHOULDER_LABELS]
            left_com_points = [markers[i][:3] for i in LEFT_COM_LABELS]

            right_shoulder = np.mean(right_shoulder_points, axis=0)
            right_com = np.mean(right_com_points, axis=0)
            left_shoulder = np.mean(left_shoulder_points, axis=0)
            left_com = np.mean(left_com_points, axis=0)

            # Flip x and y and reflect x to account for different setup
            right_shoulder[0], right_shoulder[1] = right_shoulder[1], -right_shoulder[0]
            right_com[0], right_com[1] = right_com[1], -right_com[0]
            left_shoulder[0], left_shoulder[1] = left_shoulder[1], -left_shoulder[0]
            left_com[0], left_com[1] = left_com[1], -left_com[0]

            plot_2d_arm(
                right_shoulder,
                right_com,
                "right",
                right_com_point,
                right_forward_com_point,
                right_backward_com_point,
            )
            plot_2d_arm(
                left_shoulder,
                left_com,
                "left",
                left_com_point,
                left_forward_com_point,
                left_backward_com_point,
            )

            fr_number.set_text(f"packet: {packet_number}")

            # Blitting manager only updates changed artists
            bm.update()

    except KeyboardInterrupt:
        print("Exiting...")
        socket.close()
        exit(0)


if __name__ == "__main__":
    main()
