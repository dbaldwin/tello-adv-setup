# simple example demonstrating how to control a Tello using your keyboard.
# For a more fully featured example see manual-control-pygame.py
#
# Use W, A, S, D for moving, E, Q for rotating and R, F for going up and down.
# When starting the script the Tello will takeoff, pressing ESC makes it land
#  and the script exit.

from djitellopy import Tello
import cv2

tello = Tello()
tello.connect()

tello.streamon()
frame_read = tello.get_frame_read()

print(f"Battery Life Percentage: {tello.get_battery()}")

tello.takeoff()

try:
    while True:
        # In reality you want to display frames in a separate thread. Otherwise
        #  they will freeze while the drone moves.
        img = frame_read.frame
        cv2.imshow("Tello View", img)

        key = cv2.waitKey(1) & 0xff
        if key == 27: # ESC
            break
        elif key == ord('w'):
            tello.move_forward(30)

        elif key == ord('s'):
            tello.move_back(30)

        elif key == ord('a'):
            tello.move_left(30)

        elif key == ord('d'):
            tello.move_right(30)

        elif key == ord('e'):
            tello.rotate_clockwise(30)

        elif key == ord('q'):
            tello.rotate_counter_clockwise(30)

        elif key == ord('r'):
            tello.move_up(30)

        elif key == ord('f'):
            tello.move_down(30)

        elif key == ord('l'):
            tello.land()
            break
finally:
    tello.land()

    tello.streamoff()

    cv2.destroyWindow('Tello View')
    cv2.destroyAllWindows()