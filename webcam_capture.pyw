import cv2
import os
import sys


def _get_script_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


script_dir = _get_script_dir()
image_path = os.path.join(script_dir, "webcam_capture.jpg")


def _try_set_resolution(cap, width, height):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
    # Read back what the camera actually set
    actual_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return int(actual_w), int(actual_h)


def main() -> None:
    cap = None
    try:
        # Try common backends on Windows; CAP_DSHOW often works best for webcams
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        for backend in backends:
            cap = cv2.VideoCapture(0, backend)
            if cap is not None and cap.isOpened():
                break
            try:
                if cap is not None:
                    cap.release()
            except Exception:
                pass
            cap = None

        if cap is None or not cap.isOpened():
            # Fall back to index scan if index 0 didn't work
            for idx in range(1, 5):
                cap = cv2.VideoCapture(idx)
                if cap is not None and cap.isOpened():
                    break
                try:
                    if cap is not None:
                        cap.release()
                except Exception:
                    pass
                cap = None

        if cap is None or not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        # Try a set of high resolutions (from high to lower); cameras will pick the closest supported
        preferred_resolutions = [
            (3840, 2160),  # 4K
            (1920, 1080),  # 1080p
            (1280, 720),   # 720p
            (640, 480),    # VGA fallback
        ]

        chosen_resolution = None
        for w, h in preferred_resolutions:
            actual_w, actual_h = _try_set_resolution(cap, w, h)
            # Accept if actual resolution is within 90% of requested (hardware may downscale)
            if actual_w >= int(w * 0.9) and actual_h >= int(h * 0.9):
                chosen_resolution = (actual_w, actual_h)
                break

        # If none matched, just read the current resolution
        if chosen_resolution is None:
            chosen_resolution = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        # Grab a frame
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error: Could not read frame from webcam.")
            return

        # Save with high JPEG quality (95). You can also save PNG for lossless, but JPEG with high quality reduces file size.
        ext = os.path.splitext(image_path)[1].lower()
        if ext in (".jpg", ".jpeg"):
            encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            ok = cv2.imwrite(image_path, frame, encode_params)
        else:
            # default to PNG if extension isn't jpg
            png_path = os.path.splitext(image_path)[0] + ".png"
            ok = cv2.imwrite(png_path, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 1])

        if ok:
            print(f"Image saved to {image_path}")
        else:
            print(f"Error: cv2.imwrite failed when saving to {image_path}")

    finally:
        try:
            if cap is not None:
                cap.release()
        except Exception:
            pass


if __name__ == "__main__":
    main()