# Arm Swing Visualization

## IP addresses

On the Harvard secure network, both the desktop PC for Qualisys data colletion and computer running the publisher server (`server.py`) must be connected to the network on the same way (WIFI or ETH), otherwise they won't be able to communicate between them (the first 2 sets of numbers in the IP address must be the same).

You might need to modify the IP address and make it static so that they are on the same network.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Run the server to listen to the QTM data stream and set up the publisher socket.

```bash
python server.py
```

2. Run the client to connect to the socket and visualize the arm swing.

```bash
python plot.py
```
