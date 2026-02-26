import json
import numpy as np
import matplotlib.pyplot as plt
from utils.labels import (
    RIGHT_COM_LABELS,
    LEFT_COM_LABELS,
    RIGHT_SHOULDER_LABELS,
    LEFT_SHOULDER_LABELS,
)
from utils.client import (
    setup_client_logger,
    get_qrt_data,
    connect_to_publisher,
)
from utils.blit import BlitManager


SWING_ANGLE = 160  # Desired swing angle (in degrees based on a bearing). So 0° is straight up, 90° is straight out.
SEPARATE_CONSTANT = 100  # Constant to separate the arms from the center of the screen.

# Global variables to store the calibrated values.
left_arm_length = None
right_arm_length = None
arm_length = None
left_offset = None
right_offset = None
swing_amplitude = None


def calc_target_pos(arm: str, direction: str):
    """Calculate the target position for the center of mass for the forward and backward swing.

    Args:
        arm (str): Which arm to calculate the target position for.
        direction (str): The direction of the swing (forward or backward).

    Returns:
        np.array: The target position for the center of mass.
    """

    x = (
        SEPARATE_CONSTANT + right_offset
        if arm == "right"
        else -SEPARATE_CONSTANT + left_offset
    )
    y = swing_amplitude if direction == "forward" else -swing_amplitude
    pos = np.array([x, y])

    return pos


def update_com_pos(com_plot, shoulder, com, arm: str):
    """Update the center of mass position on the plot.

    Args:
        com_plot (matplotlib plot): The plot of the center of mass.
        shoulder (np.array): The shoulder position.
        com (np.array): The center of mass position.
        arm (str): The arm to update the center of mass for.
    """
    sep_constant = 100 if arm == "right" else -100

    # Calculate the center of mass position relative to the shoulder position.
    com[0] = com[0] - shoulder[0] + sep_constant
    com[1] = com[1] - shoulder[1]

    # Update the center of mass position.
    com_plot.set_data([com[0]], [com[1]])


def load_calibration():
    """Read the calibration file and set the global variables."""
    try:
        with open("calibration.json", "r") as f:
            # Set global static variables from the calibration file
            global \
                left_arm_length, \
                right_arm_length, \
                arm_length, \
                left_offset, \
                right_offset
            data = json.load(f)

            left_arm_length = data["left_arm_length"]
            right_arm_length = data["right_arm_length"]
            arm_length = data["arm_length"]
            left_offset = data["left_offset"]
            right_offset = data["right_offset"]

    except FileNotFoundError:
        print("No calibration file found")


def main():
    """Main function to run the 2D arm swing visualization."""

    # Load calibration and initialize variables.
    load_calibration()

    # Set the swing amplitude based on the desired swing angle and calibrated arm length (avg of left and right).
    global swing_amplitude
    swing_amplitude = np.sin(np.radians(SWING_ANGLE)) * arm_length

    # Connect to the publisher.
    client_logger = setup_client_logger()
    socket = connect_to_publisher(logger=client_logger)

    # Set up the plot.
    fig, ax = plt.subplots(figsize=(8, 8))

    ax.set_xlim(-250, 250)
    ax.set_ylim(-250, 250)
    ax.set_aspect("equal")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(f"2D Arm Swing Visualization - Angle: {SWING_ANGLE}°")

    # Display the packet number in the top left.
    packet_number_plot = ax.annotate(
        "0",
        (0, 1),
        xycoords="axes fraction",
        xytext=(10, -10),
        textcoords="offset points",
        ha="left",
        va="top",
        animated=True,
    )

    # Calculate where to plot the center of mass targets for the forward and backward swing.
    rf_target_pos = calc_target_pos("right", "forward")
    rb_target_pos = calc_target_pos("right", "backward")
    lf_target_pos = calc_target_pos("left", "forward")
    lb_target_pos = calc_target_pos("left", "backward")

    # Display the center of masses for the arms and the target center of masses for the forward and backward swing.
    (left_com_plot,) = ax.plot(0, 0, "bo", markersize=20, animated=True)
    (right_com_plot,) = ax.plot(0, 0, "ro", markersize=20, animated=True)

    # Plot the target center of masses for the forward and backward swing.
    ax.plot(
        lf_target_pos[0],
        lf_target_pos[1],
        "bo",  # Blue circle
        markerfacecolor="none",
        markeredgecolor="b",
        markersize=40,
        alpha=0.7,
    )
    ax.plot(
        lb_target_pos[0],
        lb_target_pos[1],
        "bo",
        markerfacecolor="none",
        markeredgecolor="b",
        markersize=40,
        alpha=0.7,
    )
    ax.plot(
        rf_target_pos[0],
        rf_target_pos[1],
        "ro",  # Red circle
        markerfacecolor="none",
        markeredgecolor="r",
        markersize=40,
        alpha=0.7,
    )
    ax.plot(
        rb_target_pos[0],
        rb_target_pos[1],
        "ro",
        markerfacecolor="none",
        markeredgecolor="r",
        markersize=40,
        alpha=0.7,
    )

    # Initialize the blitting manager to only update changed artists on rerenders.
    bm = BlitManager(
        fig.canvas,
        [
            packet_number_plot,
            left_com_plot,
            right_com_plot,
        ],
    )

    plt.ion()  # Turn on interactive mode
    plt.show(block=False)

    # Pause for some time to ensure that at least 1 frame is displayed and cached for future renders.
    plt.pause(0.1)

    packet_number = 0

    try:
        # Continuously fetch data from the publisher and update the plot.
        while True:
            frame_number, markers, _ = get_qrt_data(logger=client_logger, socket=socket)
            if frame_number is None or len(markers) == 0:
                continue

            packet_number = frame_number
            print(f"Received frame {packet_number}, {len(markers)} markers")

            # Get the shoulder and center of mass points for the right and left arms.
            right_shoulder_points = [markers[i][:3] for i in RIGHT_SHOULDER_LABELS]
            right_com_points = [markers[i][:3] for i in RIGHT_COM_LABELS]
            left_shoulder_points = [markers[i][:3] for i in LEFT_SHOULDER_LABELS]
            left_com_points = [markers[i][:3] for i in LEFT_COM_LABELS]

            # Average the shoulder and center of mass points to get the center of mass for the right and left arms.
            right_shoulder = np.mean(right_shoulder_points, axis=0)
            right_com = np.mean(right_com_points, axis=0)
            left_shoulder = np.mean(left_shoulder_points, axis=0)
            left_com = np.mean(left_com_points, axis=0)

            # Flip the x and y axes, and then reflect the y axis to get the correct orientation.
            # We need to do this to plot the arms correctly (show the swings vertically) as the markers are using different axes.
            right_shoulder[0], right_shoulder[1] = right_shoulder[1], -right_shoulder[0]
            right_com[0], right_com[1] = right_com[1], -right_com[0]
            left_shoulder[0], left_shoulder[1] = left_shoulder[1], -left_shoulder[0]
            left_com[0], left_com[1] = left_com[1], -left_com[0]

            # Update the center of mass positions on the plot.
            update_com_pos(
                right_com_plot,
                right_shoulder,
                right_com,
                "right",
            )
            update_com_pos(
                left_com_plot,
                left_shoulder,
                left_com,
                "left",
            )

            # Update and render the packet number.
            packet_number_plot.set_text(f"packet: {packet_number}")

            # Blitting manager only updates changed artists
            bm.update()

    except KeyboardInterrupt:
        print("Exiting...")
        socket.close()
        exit(0)


if __name__ == "__main__":
    main()
