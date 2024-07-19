import matplotlib.pyplot as plt
from client import (
    setup_client_logger,
    get_qrt_data,
    connect_to_publisher,
)
from utils.blit import BlitManager


FRAMES_PER_SECOND = 60
PAUSE_BETWEEN_FRAMES = 1 / FRAMES_PER_SECOND


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
    ax.set_title(f"2D Arm Swing Visualization - Client Test")

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

    bm = BlitManager(
        fig.canvas,
        [
            fr_number,
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

            fr_number.set_text(f"packet: {packet_number}")
            bm.update()

    except KeyboardInterrupt:
        print("Exiting...")
        socket.close()
        exit(0)


if __name__ == "__main__":
    main()
