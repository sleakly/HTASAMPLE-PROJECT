import cv2
import os

# Get the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "webcam_capture.jpg")

# Open the default webcam (usually device 0)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

ret, frame = cap.read()
if ret:
    cv2.imwrite(image_path, frame)
    print(f"Image saved to {image_path}")
else:
    print("Error: Could not read frame from webcam.")

cap.release()