import json
import numpy as np
from labels import (
    RIGHT_COM_LABELS,
    LEFT_COM_LABELS,
    RIGHT_SHOULDER_LABELS,
    LEFT_SHOULDER_LABELS,
)

from client import (
    setup_client_logger,
    get_qrt_data,
    connect_to_publisher,
)


def main():
    client_logger = setup_client_logger()
    socket = connect_to_publisher(logger=client_logger)

    try:
        while True:
            frame_number, markers, _ = get_qrt_data(logger=client_logger, socket=socket)
            print(f"Received frame {frame_number}, {len(markers)} markers")

            # Get the center of mass and shoulder positions for the right and left arms.
            left_com_pos = np.mean(
                np.array([markers[i][:3] for i in LEFT_COM_LABELS]), axis=0
            )
            right_com_pos = np.mean(
                np.array([markers[i][:3] for i in RIGHT_COM_LABELS]), axis=0
            )

            # Get the shoulder positions for the right and left arms.
            left_shoulder_pos = np.mean(
                np.array([markers[i][:3] for i in LEFT_SHOULDER_LABELS]), axis=0
            )
            right_shoulder_pos = np.mean(
                np.array([markers[i][:3] for i in RIGHT_SHOULDER_LABELS]), axis=0
            )

            # Calculate the arm length and offset for the right and left arms.
            left_arm_length = np.linalg.norm(left_com_pos - left_shoulder_pos)
            right_arm_length = np.linalg.norm(right_com_pos - right_shoulder_pos)

            arm_length = np.mean([left_arm_length, right_arm_length])

            # Calculate the offset of the center of mass from the shoulder for the right and left arms.
            left_offset = left_com_pos[1] - left_shoulder_pos[1]
            right_offset = right_com_pos[1] - right_shoulder_pos[1]

            print("-" * 25)
            print(f"Left Offset: {left_offset}")
            print(f"Right Offset: {right_offset}")
            print(f"Left Arm Length: {left_arm_length}")
            print(f"Right Arm Length: {right_arm_length}")
            print(f"Arm Length: {arm_length}")
            print("-" * 25)

            data = {
                "left_arm_length": left_arm_length,
                "right_arm_length": right_arm_length,
                "arm_length": arm_length,
                "left_offset": left_offset,
                "right_offset": right_offset,
            }

            # Save the calibration data to a file.
            with open("calibration.json", "w") as f:
                f.write(json.dumps(data))

    except KeyboardInterrupt:
        print("Exiting...")
        socket.close()
        exit(0)


if __name__ == "__main__":
    main()
