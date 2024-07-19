import asyncio
import qtm_rt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from labels import (
    RIGHT_COM_LABELS,
    LEFT_COM_LABELS,
    RIGHT_SHOULDER_LABELS,
    LEFT_SHOULDER_LABELS,
)

IP_ADDRESS = "140.247.112.125"
PASSWORD = "$KHU15"
DESIRED_ANGLE = 170
FRAMES_PER_SECOND = 200
PAUSE_BETWEEN_FRAMES = 1 / FRAMES_PER_SECOND

fig, ax = plt.subplots(figsize=(10, 10))
points = []


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


def plot_2d_arm(ax, shoulder, com, arm: str):
    point_size = 400
    color = "red" if arm == "right" else "blue"

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

    ax.scatter(com[0], com[1], color=color, s=point_size, zorder=10)

    arm_length = np.linalg.norm(com - shoulder)
    forward_com = calc_desired_arm_vector(shoulder, com, DESIRED_ANGLE)
    backward_com = calc_desired_arm_vector(shoulder, com, 360 - DESIRED_ANGLE)

    forward_com[1] += shoulder[1]
    backward_com[1] += shoulder[1]

    ax.scatter(
        [forward_com[0], backward_com[0]],
        [forward_com[1], backward_com[1]],
        color=[color, color],
        s=point_size,
        alpha=0.5,
        zorder=5,
    )


def update_plot(frame):
    ax.clear()
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(f"2D Arm Swing Visualization - Angle: {DESIRED_ANGLE}°")

    if len(points) == 0:
        return

    right_shoulder_points = [points[i][:3] for i in RIGHT_SHOULDER_LABELS]
    right_com_points = [points[i][:3] for i in RIGHT_COM_LABELS]
    left_shoulder_points = [points[i][:3] for i in LEFT_SHOULDER_LABELS]
    left_com_points = [points[i][:3] for i in LEFT_COM_LABELS]

    right_shoulder = np.mean(right_shoulder_points, axis=0)
    right_com = np.mean(right_com_points, axis=0)
    left_shoulder = np.mean(left_shoulder_points, axis=0)
    left_com = np.mean(left_com_points, axis=0)

    # flip x and y to account for different setup
    right_shoulder[0], right_shoulder[1] = right_shoulder[1], right_shoulder[0]
    right_com[0], right_com[1] = right_com[1], right_com[0]
    left_shoulder[0], left_shoulder[1] = left_shoulder[1], left_shoulder[0]
    left_com[0], left_com[1] = left_com[1], left_com[0]

    plot_2d_arm(ax, right_shoulder, right_com, "right")
    plot_2d_arm(ax, left_shoulder, left_com, "left")

    ax.set_xlim(750, 1250)
    ax.set_ylim(750, 1250)
    ax.set_aspect("equal")


def on_packet(packet):
    # if packet.framenumber % 5 == 0:
    global points
    _, markers = packet.get_3d_markers()
    points = [np.array([marker.x, marker.y, marker.z]) for marker in markers]
    print(f"Received data for frame {packet.framenumber}, {len(points)} markers")
    # print(points)


async def setup():
    print(f"Attempting to connect to QTM at {IP_ADDRESS}")
    try:
        connection = await asyncio.wait_for(
            qtm_rt.connect(IP_ADDRESS, version="1.8"), timeout=5.0
        )
        if connection is None:
            print("Failed to connect to QTM")
            return None
        print("Connected to QTM")
        return connection
    except asyncio.TimeoutError:
        print("Connection attempt timed out")
        return None
    except Exception as e:
        print(f"Error connecting to QTM: {e}")
        return None


async def run_qtm():
    connection = await setup()
    if connection is None:
        print("Could not set up QTM connection. Exiting QTM task.")
        return

    try:
        await connection.stream_frames(
            frames="frequency:24", components=["3d"], on_packet=on_packet
        )
    except Exception as e:
        print(f"Error during frame streaming: {e}")


async def run_animation():
    ani = FuncAnimation(
        fig,
        update_plot,
        interval=PAUSE_BETWEEN_FRAMES * 1000,
        blit=True,
        cache_frame_data=False,
    )
    plt.show(block=False)
    plt.pause(0.1)
    while True:
        plt.pause(0.1)  # Keep the plot updating
        await asyncio.sleep(0.1)  # Allow other tasks to run


async def main():
    qtm_task = asyncio.create_task(run_qtm())
    animation_task = asyncio.create_task(run_animation())
    await asyncio.gather(qtm_task, animation_task)


if __name__ == "__main__":
    asyncio.run(main())
