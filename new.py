import qtm_rt
import asyncio
import numpy as np
from collections import deque
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
FRAMES_PER_SECOND = 60
PAUSE_BETWEEN_FRAMES = 1 / FRAMES_PER_SECOND

fig, ax = plt.subplots(figsize=(10, 10))
points = deque(maxlen=1000)  # Use a deque with a maximum length

# The labels are already lists of indices, so we can use them directly
RIGHT_SHOULDER_INDICES = RIGHT_SHOULDER_LABELS
LEFT_SHOULDER_INDICES = LEFT_SHOULDER_LABELS
RIGHT_COM_INDICES = RIGHT_COM_LABELS
LEFT_COM_INDICES = LEFT_COM_LABELS


def calc_desired_arm_vector(shoulder, com, desired_angle):
    current_vector = com - shoulder
    return np.array(
        [
            com[0],
            shoulder[1]
            + np.sin(np.radians(desired_angle)) * np.linalg.norm(current_vector),
            shoulder[2]
            + np.cos(np.radians(desired_angle)) * np.linalg.norm(current_vector),
        ]
    )


def init_plot():
    ax.set_xlim(750, 1250)
    ax.set_ylim(750, 1250)
    ax.set_aspect("equal")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(f"2D Arm Swing Visualization - Angle: {DESIRED_ANGLE}°")
    return [
        ax.plot([], [], "ro")[0],
        ax.plot([], [], "bo")[0],
        ax.plot([], [], "go")[0],
        ax.plot([], [], "yo")[0],
    ]


def update_plot(frame):
    if not points:
        return []

    current_points = points[-1]

    right_shoulder = np.mean(
        [current_points[i] for i in RIGHT_SHOULDER_INDICES], axis=0
    )
    left_shoulder = np.mean([current_points[i] for i in LEFT_SHOULDER_INDICES], axis=0)
    right_com = np.mean([current_points[i] for i in RIGHT_COM_INDICES], axis=0)
    left_com = np.mean([current_points[i] for i in LEFT_COM_INDICES], axis=0)

    # Flip x and y
    right_shoulder[0], right_shoulder[1] = right_shoulder[1], right_shoulder[0]
    right_com[0], right_com[1] = right_com[1], right_com[0]
    left_shoulder[0], left_shoulder[1] = left_shoulder[1], left_shoulder[0]
    left_com[0], left_com[1] = left_com[1], left_com[0]

    # Adjust positions
    right_shoulder[0] = right_com[0] = 1100
    left_shoulder[0] = left_com[0] = 900

    right_forward = calc_desired_arm_vector(right_shoulder, right_com, DESIRED_ANGLE)
    right_backward = calc_desired_arm_vector(
        right_shoulder, right_com, 360 - DESIRED_ANGLE
    )
    left_forward = calc_desired_arm_vector(left_shoulder, left_com, DESIRED_ANGLE)
    left_backward = calc_desired_arm_vector(
        left_shoulder, left_com, 360 - DESIRED_ANGLE
    )

    plot_data = [
        ([right_com[0]], [right_com[1]]),
        ([left_com[0]], [left_com[1]]),
        ([right_forward[0], right_backward[0]], [right_forward[1], right_backward[1]]),
        ([left_forward[0], left_backward[0]], [left_forward[1], left_backward[1]]),
    ]

    for line, (x_data, y_data) in zip(ax.lines, plot_data):
        line.set_data(x_data, y_data)

    return ax.lines


def on_packet(packet):
    global points
    # if packet.framenumber % 5 == 0:
    _, markers = packet.get_3d_markers()
    points.append([np.array([marker.x, marker.y, marker.z]) for marker in markers])


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
        await connection.stream_frames(components=["3d"], on_packet=on_packet)
    except Exception as e:
        print(f"Error during frame streaming: {e}")


async def run_animation():
    ani = FuncAnimation(
        fig,
        update_plot,
        interval=PAUSE_BETWEEN_FRAMES * 1000,
        init_func=init_plot,
        blit=True,
        cache_frame_data=False,
    )
    plt.show(block=False)
    while True:
        plt.pause(0.001)
        await asyncio.sleep(0.001)


async def main():
    qtm_task = asyncio.create_task(run_qtm())
    animation_task = asyncio.create_task(run_animation())
    await asyncio.gather(qtm_task, animation_task)


if __name__ == "__main__":
    asyncio.run(main())
