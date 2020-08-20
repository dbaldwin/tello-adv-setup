# simple example demonstrating how to control a Tello using your keyboard.
# For a more fully featured example see manual-control-pygame.py
#
# Use W, A, S, D for moving, E, Q for rotating and R, F for going up and down.
# When starting the script the Tello will takeoff, pressing ESC makes it land
#  and the script exit.

from djitellopy import Tello
import cv2

# Create Tello Object
tello = Tello()

# Connect to Tello
tello.connect()

print(f"Battery Life Percentage: {tello.get_battery()}")

# Start the video Stream
tello.streamon()

# Get the frame reader
frame_reader = tello.get_frame_read()

while True:
    # In reality you want to display frames in a separate thread. Otherwise
    # they will freeze while the drone moves.

    # Read a video frame from Tello
    img = frame_reader.frame

    # Have OpenCV display the Video Frame
    cv2.imshow("Tello View", img)

    # If ESC is pressed then stop
    key = cv2.waitKey(1) & 0xff
    if key == 27: # ESC
        break

cv2.destroyWindow('Tello View')
cv2.destroyAllWindows()
tello.streamoff()





















