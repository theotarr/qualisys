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


    print("Starting animation...")
    packet_number = 0

    try:
        while True:
            markers, _ = get_qrt_data(logger=client_logger, socket=socket)
            print(f"Received frame {packet_number}, {len(markers)} markers")
            packet_number += 1

            left_com_pos = np.mean(np.array([markers[i][:3] for i in LEFT_COM_LABELS]), axis=0)
            right_com_pos = np.mean(np.array([markers[i][:3] for i in RIGHT_COM_LABELS]), axis=0)
            
            left_shoulder_pos = np.mean(np.array([markers[i][:3] for i in LEFT_SHOULDER_LABELS]), axis=0)
            right_shoulder_pos = np.mean(np.array([markers[i][:3] for i in RIGHT_SHOULDER_LABELS]), axis=0)
                
            left_arm_length = np.linalg.norm(left_com_pos - left_shoulder_pos)
            right_arm_length = np.linalg.norm(right_com_pos - right_shoulder_pos)
            
            arm_length = np.mean([left_arm_length, right_arm_length])
            
            left_offset = left_com_pos[1] - left_shoulder_pos[1]
            right_offset = right_com_pos[1] - right_shoulder_pos[1]
                
            print(f"Left COM: {left_com_pos}")
            print(f"Right COM: {right_com_pos}")
            print(f"Left Shoulder: {left_shoulder_pos}")
            print(f"Right Shoulder: {right_shoulder_pos}")
            print(f"Arm Length: {arm_length}")
            
            data = {
                'left_arm_length': left_arm_length,
                'right_arm_length': right_arm_length,
                'arm_length': arm_length,
                'left_offset': left_offset,
                'right_offset': right_offset,
                # 'left_com_pos': left_com_pos,
                # 'right_com_pos': right_com_pos,
                # 'left_shoulder_pos': left_shoulder_pos,
                # 'right_shoulder_pos': right_shoulder_pos,
            }

            # Save it to a file
            with open("calibration.json", "w") as f:
                f.write(json.dumps(data))

    except KeyboardInterrupt:
        print("Exiting...")
        socket.close()
        exit(0)


if __name__ == "__main__":
    main()
