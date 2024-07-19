# Arm Swing Visualization

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
python test_plot.py
```
