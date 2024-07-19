import c3d
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from labels import (
    RIGHT_COM_LABELS,
    LEFT_COM_LABELS,
    RIGHT_SHOULDER_LABELS,
    LEFT_SHOULDER_LABELS,
)


INITIAL_RIGHT_COM_Y = None
INITIAL_LEFT_COM_Y = None
DESIRED_ANGLE = 160
FRAMES_PER_SECOND = 200
PAUSE_BETWEEN_FRAMES = 1 / FRAMES_PER_SECOND

reader = c3d.Reader(open("data/swing.c3d", "rb"))
labels = reader.point_labels
labels = [label.strip() for label in labels]

# Pre-load all frames
all_frames = list(reader.read_frames())
points = all_frames[0][1]


def find_point_index(labels, target_label):
    return np.where(labels == target_label)[0][0]


def calc_arm_angle(shoulder, com):
    vector = com - shoulder
    angle = np.arctan2(vector[2], vector[1])
    angle -= (
        np.pi / 2
    )  # Subtract 90 degrees to make arms resting straight down 0 degrees
    bearing = (
        np.degrees(angle) + 360
    ) % 360  # Convert angle to a bearing between 0 and 360 degrees
    return bearing


def calc_desired_arm_vector(shoulder, com, desired_angle):
    """Calculate the desired arm vector given the shoulder and COM points and the desired angle. This function assumes that the desired angle is in the same X-plane as the current arm vector."""
    current_vector = com - shoulder
    desired_vector = np.array(
        [
            com[0],
            np.sin(np.radians(desired_angle)) * np.linalg.norm(current_vector),
            np.cos(np.radians(desired_angle)) * np.linalg.norm(current_vector),
        ]
    )
    return desired_vector


# def plot_points(points, labels):
#     # Plot the points in 3D
#     ax.scatter(points[:, 0], points[:, 1], points[:, 2])

#     # Set the same scale for all axes
#     max_range = max(
#         points[:, 0].max() - points[:, 0].min(),
#         points[:, 1].max() - points[:, 1].min(),
#         points[:, 2].max() - points[:, 2].min(),
#     )
#     mid_x = (points[:, 0].max() + points[:, 0].min()) * 0.5
#     mid_y = (points[:, 1].max() + points[:, 1].min()) * 0.5
#     mid_z = (points[:, 2].max() + points[:, 2].min()) * 0.5
#     ax.set_xlim(mid_x - max_range * 0.5, mid_x + max_range * 0.5)
#     ax.set_ylim(mid_y - max_range * 0.5, mid_y + max_range * 0.5)
#     ax.set_zlim(mid_z - max_range * 0.5, mid_z + max_range * 0.5)

#     # Add labels for each point
#     for label, point in zip(labels, points):
#         ax.text(point[0], point[1], point[2], label)

#     plt.show()


# def calculate_bounding_box(points):
#     x_coords = points[0]
#     y_coords = points[1]
#     z_coords = points[2]

#     min_x, max_x = np.min(x_coords), np.max(x_coords)
#     min_y, max_y = np.min(y_coords), np.max(y_coords)
#     min_z, max_z = np.min(z_coords), np.max(z_coords)

#     return (min_x, max_x), (min_y, max_y), (min_z, max_z)


# def init():
#     # ax.set_axis_off()
#     # Set initial limits based on the first frame
#     points = all_frames[0]
#     (min_x, max_x), (min_y, max_y), (min_z, max_z) = calculate_bounding_box(points)
#     padding = 0
#     max_range = np.array([max_x - min_x, max_y - min_y, max_z - min_z]).max() / 2.0
#     mid_x = (max_x + min_x) * 0.5
#     mid_y = (max_y + min_y) * 0.5
#     mid_z = (max_z + min_z) * 0.5
#     ax.set_xlim(mid_x - max_range - padding, mid_x + max_range + padding)
#     ax.set_ylim(mid_y - max_range - padding, mid_y + max_range + padding)
#     ax.set_zlim(mid_z - max_range - padding, mid_z + max_range + padding)

#     ax.margins(1)

#     return []


# def update(frame):
#     # if not frame % 2 == 0:
#     #     return []

#     ax.clear()
#     ax.margins(1)
#     ax.set_xlabel("X")
#     ax.set_ylabel("Y")
#     ax.set_zlabel("Z")
#     ax.set_title(f"Arm Swing Angle Visualization - Desired Angle: {DESIRED_ANGLE}°")
#     # ax.set_axis_off()

#     i, points, analog = all_frames[frame]

#     # Calculate bounding box
#     (min_x, max_x), (min_y, max_y), (min_z, max_z) = calculate_bounding_box(points)

#     # Add some padding
#     padding = 100  # Adjust this value as needed
#     ax.set_xlim(min_x - padding, max_x + padding)
#     ax.set_ylim(min_y - padding, max_y + padding)
#     ax.set_zlim(min_z - padding, max_z + padding)

#     # Ensure equal aspect ratio
#     max_range = np.array([max_x - min_x, max_y - min_y, max_z - min_z]).max() / 2.0
#     mid_x = (max_x + min_x) * 0.5
#     mid_y = (max_y + min_y) * 0.5
#     mid_z = (max_z + min_z) * 0.5
#     ax.set_xlim(mid_x - max_range, mid_x + max_range)
#     ax.set_ylim(mid_y - max_range, mid_y + max_range)
#     ax.set_zlim(mid_z - max_range, mid_z + max_range)

#     right_shoulder = None
#     left_shoulder = None
#     right_com = None
#     left_com = None

#     # Remove old collections
#     for collection in ax.collections:
#         collection.remove()

#     for point, label in zip(points, labels):
#         if label == "RSHO":
#             right_shoulder = point[:3]
#         elif label == "LSHO":
#             left_shoulder = point[:3]
#         elif label == "RHLE":
#             right_com = point[:3]
#         elif label == "LHLE":
#             left_com = point[:3]

#     artists = plot_arms(ax, right_shoulder, left_shoulder, right_com, left_com)
#     return artists


# def plot_arms(ax, rsho: tuple, lsho: tuple, rcom: tuple, lcom: tuple):
#     artists = []

#     # Create points for shoulders and COMs
#     point_size = 50  # Adjust this value to change the size of the points
#     rsho_point = ax.scatter(rsho[0], rsho[1], rsho[2], c="red", s=point_size)
#     lsho_point = ax.scatter(lsho[0], lsho[1], lsho[2], c="blue", s=point_size)
#     rcom_point = ax.scatter(rcom[0], rcom[1], rcom[2], c="red", s=point_size)
#     lcom_point = ax.scatter(lcom[0], lcom[1], lcom[2], c="blue", s=point_size)
#     artists.extend([rsho_point, lsho_point, rcom_point, lcom_point])

#     # Draw lines between the shoulders and COMs
#     (line1,) = ax.plot(
#         [rsho[0], rcom[0]], [rsho[1], rcom[1]], [rsho[2], rcom[2]], color="blue"
#     )
#     (line2,) = ax.plot(
#         [lsho[0], lcom[0]], [lsho[1], lcom[1]], [lsho[2], lcom[2]], color="red"
#     )
#     artists.extend([line1, line2])

#     # Calculate the angle between the shoulders and COMs
#     r_angle = calc_arm_angle(rsho, rcom)
#     l_angle = calc_arm_angle(lsho, lcom)

#     # Calculate the desired arm vectors for both the forward and backward swing
#     rf_desired_vector = calc_desired_arm_vector(rsho, rcom, DESIRED_ANGLE)
#     lf_desired_vector = calc_desired_arm_vector(lsho, lcom, DESIRED_ANGLE)
#     rb_desired_vector = calc_desired_arm_vector(rsho, rcom, 360 - DESIRED_ANGLE)
#     lb_desired_vector = calc_desired_arm_vector(lsho, lcom, 360 - DESIRED_ANGLE)

#     # Draw a dashed line straight down to represent resting arms
#     (line3,) = ax.plot(
#         [rsho[0], rsho[0]],
#         [rsho[1], rsho[1]],
#         [rsho[2], 0],
#         linestyle="--",
#         color="gray",
#     )
#     (line4,) = ax.plot(
#         [lsho[0], lsho[0]],
#         [lsho[1], lsho[1]],
#         [lsho[2], 0],
#         linestyle="--",
#         color="gray",
#     )
#     artists.extend([line3, line4])

#     # Plot lines for the desired angles and add points for desired COM positions
#     rf_desired_end = rsho + rf_desired_vector
#     lf_desired_end = lsho + lf_desired_vector
#     rb_desired_end = rsho + rb_desired_vector
#     lb_desired_end = lsho + lb_desired_vector

#     (line5,) = ax.plot(
#         [rsho[0], rf_desired_end[0]],
#         [rsho[1], rf_desired_end[1]],
#         [rsho[2], rf_desired_end[2]],
#         color="green",
#         linestyle=":",
#     )
#     (line6,) = ax.plot(
#         [lsho[0], lf_desired_end[0]],
#         [lsho[1], lf_desired_end[1]],
#         [lsho[2], lf_desired_end[2]],
#         color="green",
#         linestyle=":",
#     )
#     (line7,) = ax.plot(
#         [rsho[0], rb_desired_end[0]],
#         [rsho[1], rb_desired_end[1]],
#         [rsho[2], rb_desired_end[2]],
#         color="orange",
#         linestyle=":",
#     )
#     (line8,) = ax.plot(
#         [lsho[0], lb_desired_end[0]],
#         [lsho[1], lb_desired_end[1]],
#         [lsho[2], lb_desired_end[2]],
#         color="orange",
#         linestyle=":",
#     )

#     artists.extend([line5, line6, line7, line8])

#     # Add points for desired COM positions
#     desired_points = ax.scatter(
#         [rf_desired_end[0], lf_desired_end[0], rb_desired_end[0], lb_desired_end[0]],
#         [rf_desired_end[1], lf_desired_end[1], rb_desired_end[1], lb_desired_end[1]],
#         [rf_desired_end[2], lf_desired_end[2], rb_desired_end[2], lb_desired_end[2]],
#         c=["green", "green", "orange", "orange"],
#         s=point_size,
#         alpha=0.5,
#     )
#     artists.append(desired_points)

#     # Add text for angles
#     r_text = ax.text(rsho[0], rsho[1], rsho[2], f"R: {r_angle:.1f}°", color="blue")
#     l_text = ax.text(lsho[0], lsho[1], lsho[2], f"L: {l_angle:.1f}°", color="red")
#     artists.extend([r_text, l_text])

#     return artists


def plot_2d_arm(ax, shoulder, com, arm: str):
    artists = []
    point_size = 400
    color = "red" if arm == "right" else "blue"

    # Set the shoulder position to the center of the plot adjusted for left or right arms
    x_off = shoulder[0] - 1000
    y_off = shoulder[1] - 1000
    shoulder[0] = 1000
    shoulder[1] = 1000

    # Set the COM position relative to the shoulder
    com[0] -= x_off
    com[1] -= y_off

    if arm == "left":
        com[0] -= 100
        shoulder[0] -= 100
    else:
        com[0] += 100
        shoulder[0] += 100

    # Plot current COM
    com_point = ax.scatter(com[0], com[1], color=color, s=point_size, zorder=10)
    artists.append(com_point)

    # Calculate and plot desired COM positions
    arm_length = np.linalg.norm(com - shoulder)
    forward_com = calc_desired_arm_vector(shoulder, com, DESIRED_ANGLE)
    backward_com = calc_desired_arm_vector(shoulder, com, 360 - DESIRED_ANGLE)

    forward_com[1] += shoulder[1]
    backward_com[1] += shoulder[1]

    # print("com", com)
    # print("forward_com", forward_com)
    # print("backward_com", backward_com)

    desired_com_points = ax.scatter(
        [forward_com[0], backward_com[0]],
        [forward_com[1], backward_com[1]],
        color=[color, color],
        s=point_size,
        alpha=0.5,
        zorder=5,
    )
    artists.append(desired_com_points)

    # # Add angle labels
    # current_angle = np.degrees(np.arctan2(com[1] - shoulder[1], com[0] - shoulder[0]))
    # angle_text = ax.text(
    #     shoulder[0],
    #     shoulder[1],
    #     f"{current_angle:.1f}°",
    #     color=color,
    #     fontsize=8,
    #     ha="right",
    #     va="bottom",
    # )
    # artists.append(angle_text)

    # # Label the points
    # ax.text(
    #     shoulder[0],
    #     shoulder[1],
    #     "Shoulder",
    #     color="black",
    #     fontsize=8,
    #     ha="right",
    #     va="bottom",
    # )
    # ax.text(
    #     backward_com[0],
    #     backward_com[1],
    #     "Back Swing Target",
    #     color="black",
    #     fontsize=8,
    #     ha="right",
    #     va="bottom",
    # )
    # ax.text(
    #     forward_com[0],
    #     forward_com[1],
    #     "Forward Swing Target",
    #     color="black",
    #     fontsize=8,
    #     ha="right",
    #     va="bottom",
    # )

    return artists


def update_2d(frame):
    ax.clear()
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(f"2D Arm Swing Visualization - Angle: {DESIRED_ANGLE}°")

    # i, points, analog = all_frames[frame]

    right_shoulder = None
    right_com = None
    left_shoulder = None
    left_com = None

    right_shoulder_points = []
    right_com_points = []
    left_shoulder_points = []
    left_com_points = []

    for i in RIGHT_SHOULDER_LABELS:
        right_shoulder_points.append(points[i][:3])
    for i in RIGHT_COM_LABELS:
        right_com_points.append(points[i][:3])
    for i in LEFT_COM_LABELS:
        left_com_points.append(points[i][:3])
    for i in LEFT_SHOULDER_LABELS:
        left_shoulder_points.append(points[i][:3])

    right_shoulder = np.mean(right_shoulder_points, axis=0)
    right_com = np.mean(right_com_points, axis=0)
    left_shoulder = np.mean(left_shoulder_points, axis=0)
    left_com = np.mean(left_com_points, axis=0)

    # flip x and y to account for different setup
    new_right_shoulder = right_shoulder.copy()
    new_right_com = right_com.copy()
    new_left_shoulder = left_shoulder.copy()
    new_left_com = left_com.copy()

    right_shoulder[0] = new_right_shoulder[1]
    right_shoulder[1] = new_right_shoulder[0]
    right_com[0] = new_right_com[1]
    right_com[1] = new_right_com[0]

    left_shoulder[0] = new_left_shoulder[1]
    left_shoulder[1] = new_left_shoulder[0]
    left_com[0] = new_left_com[1]
    left_com[1] = new_left_com[0]

    if right_shoulder is not None and right_com is not None:
        artists = []

        plot_2d_arm(ax, right_shoulder, right_com, "right")
        plot_2d_arm(ax, left_shoulder, left_com, "left")

        # Set axis limits
        padding = 100
        ax.set_xlim(750, 1250)
        ax.set_ylim(750, 1250)

        ax.set_aspect("equal")
        return artists

    return []


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(10, 10))

    num_frames = len(all_frames)
    ani = FuncAnimation(
        fig,
        update_2d,
        frames=num_frames,
        interval=PAUSE_BETWEEN_FRAMES * 1000,
        blit=False,
        repeat=False,
    )

    plt.show()


# if __name__ == "__main__":
#     fig = plt.figure(figsize=(10, 10))
#     ax = fig.add_subplot(111, projection="3d")

#     num_frames = len(all_frames)
#     ani = FuncAnimation(
#         fig,
#         update,
#         frames=num_frames,
#         init_func=init,
#         blit=True,
#         interval=PAUSE_BETWEEN_FRAMES * 1000,
#         repeat=False,
#     )

#     plt.show()
