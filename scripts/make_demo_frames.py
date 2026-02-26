"""Generate simple frame images from the bundled C3D demo for README media.

This script intentionally avoids heavy plotting deps so it runs in fresh envs.
"""

from pathlib import Path

import c3d
import numpy as np

INPUT = Path("data/arm_swing.c3d")
OUT_DIR = Path("docs/assets/demo_frames")
FRAME_STEP = 5
MAX_FRAMES = 220
WIDTH = 960
HEIGHT = 540

BG = np.array([13, 17, 23], dtype=np.uint8)      # github dark-ish
DOT = np.array([88, 166, 255], dtype=np.uint8)   # blue
TEXT_BAR = np.array([22, 27, 34], dtype=np.uint8)


def draw_dot(canvas: np.ndarray, x: int, y: int, r: int = 3) -> None:
    h, w, _ = canvas.shape
    x0, x1 = max(0, x - r), min(w - 1, x + r)
    y0, y1 = max(0, y - r), min(h - 1, y + r)
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            if (xx - x) ** 2 + (yy - y) ** 2 <= r * r:
                canvas[yy, xx] = DOT


def write_ppm(path: Path, frame: np.ndarray) -> None:
    # Binary PPM (P6)
    h, w, _ = frame.shape
    with path.open("wb") as f:
        f.write(f"P6\n{w} {h}\n255\n".encode("ascii"))
        f.write(frame.tobytes())


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    frames = []
    xs, ys = [], []

    with INPUT.open("rb") as f:
        reader = c3d.Reader(f)
        for i, points, _ in reader.read_frames():
            if i % FRAME_STEP != 0:
                continue
            pts = np.array(points[:, :2], dtype=float)
            pts = pts[~np.isnan(pts).any(axis=1)]
            if pts.size == 0:
                continue
            frames.append((i, pts))
            xs.extend(pts[:, 0].tolist())
            ys.extend(pts[:, 1].tolist())
            if len(frames) >= MAX_FRAMES:
                break

    if not frames:
        raise RuntimeError("No frames found in C3D demo file")

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    pad_x = (max_x - min_x) * 0.1 or 1.0
    pad_y = (max_y - min_y) * 0.1 or 1.0
    min_x -= pad_x
    max_x += pad_x
    min_y -= pad_y
    max_y += pad_y

    plot_top = 48
    plot_h = HEIGHT - plot_top

    for idx, (frame_no, pts) in enumerate(frames):
        canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        canvas[:, :] = BG
        canvas[:plot_top, :] = TEXT_BAR

        norm_x = (pts[:, 0] - min_x) / (max_x - min_x + 1e-9)
        norm_y = (pts[:, 1] - min_y) / (max_y - min_y + 1e-9)

        px = (norm_x * (WIDTH - 1)).astype(int)
        py = (plot_top + (1.0 - norm_y) * (plot_h - 1)).astype(int)

        for x, y in zip(px, py):
            draw_dot(canvas, int(x), int(y), r=3)

        # tiny progress indicator bar to imply motion in static overlay region
        prog = int((idx + 1) / len(frames) * WIDTH)
        canvas[plot_top - 6:plot_top - 2, :prog] = np.array([63, 185, 80], dtype=np.uint8)

        out = OUT_DIR / f"frame_{idx:04d}.ppm"
        write_ppm(out, canvas)

    print(f"Wrote {len(frames)} PPM frames to {OUT_DIR}")


if __name__ == "__main__":
    main()
