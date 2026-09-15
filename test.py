import os
import time

import cv2
from pypresence import Presence
from tqdm import tqdm

CLIENT_ID = "1549416655522627644"

GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/YOUR_USERNAME/"
    "discord-frames/main/frames/badapple"
)


def setup_folders():
    os.makedirs("videos", exist_ok=True)
    os.makedirs("frames", exist_ok=True)


def slice_video(video_name, frame_count=150, quality=90, size=512):
    folder_name = os.path.splitext(video_name)[0]
    output_dir = os.path.join("frames", folder_name)
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(os.path.join("videos", video_name))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        cap.release()
        raise RuntimeError("Could not read video.")

    frame_indices = [
        round(i * (total_frames - 1) / (frame_count - 1))
        for i in range(frame_count)
    ]

    compression = round((100 - quality) / 100 * 9)

    for index, frame_position in enumerate(
        tqdm(frame_indices, desc="Extracting frames")
    ):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)

        success, frame = cap.read()

        if not success:
            print(f"Failed to read frame {frame_position}")
            continue

        h, w = frame.shape[:2]
        side = min(w, h)

        x = (w - side) // 2
        y = (h - side) // 2

        frame = cv2.resize(
            frame[y:y + side, x:x + side],
            (size, size)
        )

        cv2.imwrite(
            os.path.join(output_dir, f"frame_{index:03d}.png"),
            frame,
            [cv2.IMWRITE_PNG_COMPRESSION, compression]
        )

    cap.release()

    print(f"Saved {frame_count} frames to {output_dir}/")


def render_folder(folder_name, fps=1):
    frame_dir = os.path.join("frames", folder_name)

    frames = sorted(
        f for f in os.listdir(frame_dir)
        if f.startswith("frame_") and f.endswith(".png")
    )

    if not frames:
        raise RuntimeError(f"No frames found in {frame_dir}")

    rpc = Presence(CLIENT_ID)
    rpc.connect()

    idx = 0
    start_time = time.time()
    interval = 1 / fps

    try:
        while True:
            frame_name = os.path.splitext(frames[idx])[0]

            image_url = f"{GITHUB_RAW_BASE}/{frame_name}.png"

            try:
                rpc.update(
                    details="Working in Autodesk Inventor",
                    state="Modeling",
                    large_image=image_url,
                    large_text="Autodesk Inventor",
                    start=start_time,
                )

                print(f"Showing {frame_name}")

            except Exception as e:
                print(f"Update failed on {frame_name}: {e}")

            idx = (idx + 1) % len(frames)
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopping...")
        rpc.close()


if __name__ == "__main__":
    setup_folders()

    # Run this ONCE to generate the 150 frames:
    slice_video("badapple2.mp4", frame_count=150, quality=90)

    #render_folder("badapple", fps=1)