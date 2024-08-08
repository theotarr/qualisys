# Arm Swing Visualization

## IP addresses

On the "Harvard Secure" network, both the desktop PC for Qualisys data colletion and computer running the publisher server (`server.py`) must be connected to the network the same way (WIFI or Ethernet), otherwise they won't be able to communicate. To check that the computers can connect they must have matching first 2 sets of numbers in their IP addresses.

You might need to modify the IP address and make them static so that they are on the same network.

## Demo

To run a demo version of this visualization, run `python demo_server.py` and then run `python plot.py` to see a playback of one data collection interval.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Run the `server.py` file to connect to the Qualisys data stream. This will also set up the publisher socket so the client (`plot.py`) can recieve data syncronously.

```bash
python server.py
```

2. Run the `calibrate.py` file to calibrate all static measurements (arm lengths and arms visualization offsets).

```bash
python calibrate.py
```

While this file is running, you should see information logged to the terminal

**Wait until your subject has their arms at a resting position and then stop running the program.** This will save the last frame of data as the measurements for the visualization.

3. Run the `plot.py` file client to connect to the socket and visualize the arm swing in real-time.

```bash
python plot.py
```