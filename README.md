# qualisys

Real-time infrared marker tracking + visualization pipeline using **Qualisys QTM**, a lightweight **ZeroMQ publisher**, and a Python visualization client.

This repo provides two end-to-end workflows:

1. **Live mode**: stream marker data directly from QTM.
2. **Demo mode**: replay bundled C3D sample data so anyone can run the project without lab hardware.

---

## What this repo does

- Connects to QTM and subscribes to real-time 3D marker frames.
- Publishes marker frames over ZeroMQ so multiple clients can subscribe.
- Calibrates arm parameters from streamed marker data.
- Renders a real-time 2D arm swing visualization from infrared marker positions.

---

## Architecture

```text
QTM (live RT stream) OR C3D replay (demo_server.py)
                  |
                  v
         server.py / demo_server.py  (ZeroMQ PUB)
                  |
                  v
      calibrate.py + plot.py + test clients (ZeroMQ SUB)
```

The publisher/subscriber split keeps data acquisition independent from visualization and makes the pipeline easy to extend.

---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional: copy env template:

```bash
cp .env.example .env
```

Then export any variables you need from `.env`.

---

## Quickstart (demo mode, no hardware required)

### Terminal 1: run demo publisher

```bash
python demo_server.py
```

### Terminal 2: calibrate

```bash
python calibrate.py
```

Let it run for a few seconds while the replay is active, then stop it (`Ctrl+C`).
This saves `calibration.json`.

### Terminal 3: visualize

```bash
python plot.py
```

You should see arm center-of-mass points update in real time against target swing markers.

---

## Live mode (QTM)

### 1) Ensure network connectivity

Machine running `server.py` and machine running QTM must be able to reach each other on the same network. If needed, set static IPs.

### 2) Set server env vars

```bash
export QTM_IP=127.0.0.1          # Replace with QTM host IP
export STREAM_FREQUENCY=40
export PUBLISH_BIND=tcp://*:5555
```

### 3) Start live publisher

```bash
python server.py
```

### 4) Calibrate + visualize

In separate terminals:

```bash
python calibrate.py
python plot.py
```

---

## Configuration

Environment variables:

- `QTM_IP` (default: `127.0.0.1`): QTM host IP for live mode.
- `QTM_RT_VERSION` (default: `1.8`): RT protocol version for `qtm_rt.connect`.
- `STREAM_FREQUENCY` (default: `40`): Live streaming frequency in Hz.
- `PUBLISH_BIND` (default: `tcp://*:5555`): ZeroMQ bind address for publisher.
- `DEMO_C3D_PATH` (default: `data/arm_swing.c3d`): Demo replay source file.
- `DEMO_FPS` (default: `40`): Demo playback output FPS.
- `DEMO_FRAME_STEP` (default: `5`): Frame downsampling step for replay.
- `PUBLISHER_SOCKET` (default: `tcp://127.0.0.1:5555`): Subscriber endpoint used by clients.

---

## Repo structure

- `server.py`: live QTM -> ZeroMQ publisher.
- `demo_server.py`: C3D replay -> ZeroMQ publisher.
- `calibrate.py`: computes arm lengths + offsets from marker data.
- `plot.py`: real-time 2D arm swing visualization.
- `utils/client.py`: subscriber + frame decoding helpers.
- `tests/`: simple connectivity/stream smoke scripts.

---

## Troubleshooting

### No frames received in client

- Confirm publisher is running (`server.py` or `demo_server.py`).
- Verify endpoint alignment:
  - publisher bind: `PUBLISH_BIND`
  - subscriber connect: `PUBLISHER_SOCKET`
- Ensure firewall/network rules allow the selected port.

### Can connect to QTM but no marker data

- Confirm QTM is actively streaming 3D markers.
- Verify marker set/labels are present and tracked.
- Check `QTM_IP` and RT protocol version (`QTM_RT_VERSION`).

### Visualization looks wrong / offset

- Re-run `calibrate.py` and keep a neutral arm posture before stopping.
- Ensure marker label mapping in `utils/labels.py` matches your marker setup.

---

## Open source readiness notes

To make this repository public and easy for external contributors:

- ✅ Include demo replay path (`demo_server.py`) so contributors can run without lab hardware.
- ✅ Keep secrets out of source code (use environment variables; no passwords in repo).
- ✅ Add calibration + troubleshooting documentation.
- ⏭️ Recommended next: add screenshots/GIF of the visualization in action.

---

## License

Add a `LICENSE` file before making this repo public.