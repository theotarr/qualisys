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


DESIRED_ANGLE = 170
FRAMES_PER_SECOND = 60
PAUSE_BETWEEN_FRAMES = 1 / FRAMES_PER_SECOND


def calc_desired_arm_vector(shoulder, com, desired_angle):
    current_vector = com - shoulder
    desired_vector = np.array(
        [
            com[0],
            np.sin(np.radians(desired_angle)) * np.linalg.norm(current_vector),
            np.cos(np.radians(desired_angle)) * np.linalg.norm(current_vector),
        ]
    )
    return desired_vector


def plot_2d_arm(
    shoulder, com, arm: str, com_point, forward_com_point, backward_com_point
):
    x_off = shoulder[0] - 1000
    y_off = shoulder[1] - 1000
    shoulder[0] = 1000
    shoulder[1] = 1000

    com[0] -= x_off
    com[1] -= y_off

    if arm == "left":
        com[0] -= 100
        shoulder[0] -= 100
    else:
        com[0] += 100
        shoulder[0] += 100

    # ax.scatter(com[0], com[1], color=color, s=point_size, zorder=10)
    com_point.set_data(com[0], com[1])

    # arm_length = np.linalg.norm(com - shoulder)
    forward_com = calc_desired_arm_vector(shoulder, com, DESIRED_ANGLE)
    backward_com = calc_desired_arm_vector(shoulder, com, 360 - DESIRED_ANGLE)

    forward_com[1] += shoulder[1]
    backward_com[1] += shoulder[1]

    # Update the forward and backward com points
    forward_com_point.set_data(forward_com[0], forward_com[1])
    backward_com_point.set_data(backward_com[0], backward_com[1])
    # ax.scatter(
    #     [forward_com[0], backward_com[0]],
    #     [forward_com[1], backward_com[1]],
    #     color=[color, color],
    #     s=point_size,
    #     alpha=0.5,
    #     zorder=5,
    # )


def main():
    client_logger = setup_client_logger()
    socket = connect_to_publisher(logger=client_logger)

    fig, ax = plt.subplots()

    # Set up the plot
    ax.set_xlim(750, 1250)
    ax.set_ylim(750, 1250)
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
    (left_com_point,) = ax.plot(0, 0, "bo", animated=True)
    (left_forward_com_point,) = ax.plot(0, 0, "bo", alpha=0.7, animated=True)
    (left_backward_com_point,) = ax.plot(0, 0, "bo", alpha=0.7, animated=True)

    (right_com_point,) = ax.plot(0, 0, "ro", animated=True)
    (right_forward_com_point,) = ax.plot(0, 0, "ro", alpha=0.7, animated=True)
    (right_backward_com_point,) = ax.plot(0, 0, "ro", alpha=0.7, animated=True)

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
            plt.pause(PAUSE_BETWEEN_FRAMES)
            markers, _ = get_qrt_data(logger=client_logger, socket=socket)
            packet_number += 1
            print(f"Received data for frame {packet_number}, {len(markers)} markers")

            # right_shoulder_points = [markers[i][:3] for i in RIGHT_SHOULDER_LABELS]
            # right_com_points = [markers[i][:3] for i in RIGHT_COM_LABELS]
            # left_shoulder_points = [markers[i][:3] for i in LEFT_SHOULDER_LABELS]
            # left_com_points = [markers[i][:3] for i in LEFT_COM_LABELS]

            # right_shoulder = np.mean(right_shoulder_points, axis=0)
            # right_com = np.mean(right_com_points, axis=0)
            # left_shoulder = np.mean(left_shoulder_points, axis=0)
            # left_com = np.mean(left_com_points, axis=0)

            # # Flip x and y to account for different setup
            # right_shoulder[0], right_shoulder[1] = right_shoulder[1], right_shoulder[0]
            # right_com[0], right_com[1] = right_com[1], right_com[0]
            # left_shoulder[0], left_shoulder[1] = left_shoulder[1], left_shoulder[0]
            # left_com[0], left_com[1] = left_com[1], left_com[0]

            # plot_2d_arm(
            #     right_shoulder,
            #     right_com,
            #     "right",
            #     right_com_point,
            #     right_forward_com_point,
            #     right_backward_com_point,
            # )
            # plot_2d_arm(
            #     left_shoulder,
            #     left_com,
            #     "left",
            #     left_com_point,
            #     left_forward_com_point,
            #     left_backward_com_point,
            # )

            fr_number.set_text(f"packet: {packet_number}")

            # Blitting manager only updates changed artists
            bm.update()

    except KeyboardInterrupt:
        print("Exiting...")
        socket.close()
        exit(0)


if __name__ == "__main__":
    main()
