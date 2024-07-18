import c3d
import time
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d.art3d as art3d


DESIRED_ANGLE = 170
FRAMES_PER_SECOND = 200
PAUSE_BETWEEN_FRAMES = 1 / FRAMES_PER_SECOND

reader = c3d.Reader(open("data/pre_walk.c3d", "rb"))
labels = reader.point_labels

# Pre-load all frames
all_frames = list(reader.read_frames())
points = all_frames[0][1]

# Store the last 10 frame times for FPS calculation
frame_times = deque(maxlen=10)  # Store the last 10 frame times
last_frame_time = time.time()


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
            0,
            np.sin(np.radians(desired_angle)) * np.linalg.norm(current_vector),
            np.cos(np.radians(desired_angle)) * np.linalg.norm(current_vector),
        ]
    )
    return desired_vector


def plot_points(points, labels):
    # Plot the points in 3D
    ax.scatter(points[:, 0], points[:, 1], points[:, 2])

    # Set the same scale for all axes
    max_range = max(
        points[:, 0].max() - points[:, 0].min(),
        points[:, 1].max() - points[:, 1].min(),
        points[:, 2].max() - points[:, 2].min(),
    )
    mid_x = (points[:, 0].max() + points[:, 0].min()) * 0.5
    mid_y = (points[:, 1].max() + points[:, 1].min()) * 0.5
    mid_z = (points[:, 2].max() + points[:, 2].min()) * 0.5
    ax.set_xlim(mid_x - max_range * 0.5, mid_x + max_range * 0.5)
    ax.set_ylim(mid_y - max_range * 0.5, mid_y + max_range * 0.5)
    ax.set_zlim(mid_z - max_range * 0.5, mid_z + max_range * 0.5)

    # Add labels for each point
    for label, point in zip(labels, points):
        ax.text(point[0], point[1], point[2], label)

    plt.show()


def calculate_bounding_box(points):
    x_coords = points[0]
    y_coords = points[1]
    z_coords = points[2]

    min_x, max_x = np.min(x_coords), np.max(x_coords)
    min_y, max_y = np.min(y_coords), np.max(y_coords)
    min_z, max_z = np.min(z_coords), np.max(z_coords)

    return (min_x, max_x), (min_y, max_y), (min_z, max_z)


def init():
    # ax.set_axis_off()
    # Set initial limits based on the first frame
    points = all_frames[0]
    (min_x, max_x), (min_y, max_y), (min_z, max_z) = calculate_bounding_box(points)
    padding = 0
    max_range = np.array([max_x - min_x, max_y - min_y, max_z - min_z]).max() / 2.0
    mid_x = (max_x + min_x) * 0.5
    mid_y = (max_y + min_y) * 0.5
    mid_z = (max_z + min_z) * 0.5
    ax.set_xlim(mid_x - max_range - padding, mid_x + max_range + padding)
    ax.set_ylim(mid_y - max_range - padding, mid_y + max_range + padding)
    ax.set_zlim(mid_z - max_range - padding, mid_z + max_range + padding)

    ax.margins(1)
    
    return []


def update(frame):
    # if not frame % 2 == 0:
    #     return []
    
    ax.clear()
    ax.margins(1)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(f"Arm Swing Angle Visualization - Desired Angle: {DESIRED_ANGLE}°")
    # ax.set_axis_off()

    i, points, analog = all_frames[frame]

    # Calculate bounding box
    (min_x, max_x), (min_y, max_y), (min_z, max_z) = calculate_bounding_box(points)

    # Add some padding
    padding = 100  # Adjust this value as needed
    ax.set_xlim(min_x - padding, max_x + padding)
    ax.set_ylim(min_y - padding, max_y + padding)
    ax.set_zlim(min_z - padding, max_z + padding)

    # Ensure equal aspect ratio
    max_range = np.array([max_x - min_x, max_y - min_y, max_z - min_z]).max() / 2.0
    mid_x = (max_x + min_x) * 0.5
    mid_y = (max_y + min_y) * 0.5
    mid_z = (max_z + min_z) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    right_shoulder = None
    left_shoulder = None
    right_com = None
    left_com = None
    
    # Remove old collections
    for collection in ax.collections:
        collection.remove()
    

    for point, label in zip(points, labels):
        if label == "RSHO":
            right_shoulder = point[:3]
        elif label == "LSHO":
            left_shoulder = point[:3]
        elif label == "RHLE":
            right_com = point[:3]
        elif label == "LHLE":
            left_com = point[:3]

    artists = plot_arms(ax, right_shoulder, left_shoulder, right_com, left_com)
    return artists


def plot_arms(ax, rsho: tuple, lsho: tuple, rcom: tuple, lcom: tuple):
    artists = []

    # Create points for shoulders and COMs
    point_size = 50  # Adjust this value to change the size of the points
    rsho_point = ax.scatter(rsho[0], rsho[1], rsho[2], c="red", s=point_size)
    lsho_point = ax.scatter(lsho[0], lsho[1], lsho[2], c="blue", s=point_size)
    rcom_point = ax.scatter(rcom[0], rcom[1], rcom[2], c="red", s=point_size)
    lcom_point = ax.scatter(lcom[0], lcom[1], lcom[2], c="blue", s=point_size)
    artists.extend([rsho_point, lsho_point, rcom_point, lcom_point])

    # Draw lines between the shoulders and COMs
    line1, = ax.plot([rsho[0], rcom[0]], [rsho[1], rcom[1]], [rsho[2], rcom[2]], color="blue")
    line2, = ax.plot([lsho[0], lcom[0]], [lsho[1], lcom[1]], [lsho[2], lcom[2]], color="red")
    artists.extend([line1, line2])

    # Calculate the angle between the shoulders and COMs
    r_angle = calc_arm_angle(rsho, rcom)
    l_angle = calc_arm_angle(lsho, lcom)
    
    # Calculate the desired arm vectors for both the forward and backward swing
    rf_desired_vector = calc_desired_arm_vector(rsho, rcom, DESIRED_ANGLE)
    lf_desired_vector = calc_desired_arm_vector(lsho, lcom, DESIRED_ANGLE)
    rb_desired_vector = calc_desired_arm_vector(rsho, rcom, 360 - DESIRED_ANGLE)
    lb_desired_vector = calc_desired_arm_vector(lsho, lcom, 360 - DESIRED_ANGLE)

    # Draw a dashed line straight down to represent resting arms
    line3, = ax.plot([rsho[0], rsho[0]], [rsho[1], rsho[1]], [rsho[2], 0], linestyle="--", color="gray")
    line4, = ax.plot([lsho[0], lsho[0]], [lsho[1], lsho[1]], [lsho[2], 0], linestyle="--", color="gray")
    artists.extend([line3, line4])

    # Plot lines for the desired angles and add points for desired COM positions
    rf_desired_end = rsho + rf_desired_vector
    lf_desired_end = lsho + lf_desired_vector
    rb_desired_end = rsho + rb_desired_vector
    lb_desired_end = lsho + lb_desired_vector
    
    line5, = ax.plot([rsho[0], rf_desired_end[0]], [rsho[1], rf_desired_end[1]], [rsho[2], rf_desired_end[2]], color="green", linestyle=":")
    line6, = ax.plot([lsho[0], lf_desired_end[0]], [lsho[1], lf_desired_end[1]], [lsho[2], lf_desired_end[2]], color="green", linestyle=":")
    line7, = ax.plot([rsho[0], rb_desired_end[0]], [rsho[1], rb_desired_end[1]], [rsho[2], rb_desired_end[2]], color="orange", linestyle=":")
    line8, = ax.plot([lsho[0], lb_desired_end[0]], [lsho[1], lb_desired_end[1]], [lsho[2], lb_desired_end[2]], color="orange", linestyle=":")
    
    artists.extend([line5, line6, line7, line8])

    # Add points for desired COM positions
    desired_points = ax.scatter([rf_desired_end[0], lf_desired_end[0], rb_desired_end[0], lb_desired_end[0]],
                                [rf_desired_end[1], lf_desired_end[1], rb_desired_end[1], lb_desired_end[1]],
                                [rf_desired_end[2], lf_desired_end[2], rb_desired_end[2], lb_desired_end[2]],
                                c=['green', 'green', 'orange', 'orange'], s=point_size, alpha=0.5)
    artists.append(desired_points)

    # Add text for angles
    r_text = ax.text(rsho[0], rsho[1], rsho[2], f"R: {r_angle:.1f}°", color="blue")
    l_text = ax.text(lsho[0], lsho[1], lsho[2], f"L: {l_angle:.1f}°", color="red")
    artists.extend([r_text, l_text])

    return artists
if __name__ == "__main__":
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")

    num_frames = len(all_frames)
    ani = FuncAnimation(
        fig,
        update,
        frames=num_frames,
        init_func=init,
        blit=True,
        interval=PAUSE_BETWEEN_FRAMES * 1000,
        repeat=False,
    )

    plt.show()
