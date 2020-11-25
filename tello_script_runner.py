import cv2
from djitellopy import Tello
import signal
import sys
import time
from datetime import datetime
import argparse
import importlib
import logging
from imutils.video import VideoStream
import imutils
import threading
import queue
import traceback

FORMAT = '%(asctime)-15s %(levelname)-10s %(message)s'
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger()

tello = None
video_writer = None
local_video_stream = None

# maximum number of
MAX_VIDEO_Q_DEPTH = 10

# add a little delay to throttle the number of video frames
# put into the video queue
show_video_per_second = 0.3


# This is hard coded because if the image gets too big then
# the lag in the video stream gets very pronounced.  This is
# parameter that will be system configured and the user will
# not be allowed change it at run time
IMAGE_WIDTH = 500

# function to handle keyboard interrupt
def signal_handler(sig, frame):
    global video_writer

    shutdown_gracefully()

    sys.exit(-1)


def shutdown_gracefully():
    global video_writer
    if tello:
        try:
            tello.end()
        except:
            pass

    if video_writer:
        try:
            LOGGER.debug("**** RELEASE VIDEO WRITER")
            video_writer.release()
            video_writer = None
        except:
            pass

    if local_video_stream:
        try:
            local_video_stream.stop()
        except:
            pass


tello_image = None


def _display_text(image, text, bat_left):
    cv2.putText(image, text, (50, int(image.shape[0]*0.90)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255, 0, 0), 2, cv2.LINE_AA)  #

    cv2.putText(image, f"Battery: {bat_left}%", (int(image.shape[1]*0.55), 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255, 0, 0), 2, cv2.LINE_AA)

    cv2.imshow("Keyboard Cmds", image)
    key = cv2.waitKey(150) & 0xff

    return key

battery_update_timestamp = 0
battery_left = "??"
last_command_timestamp = 0
last_command = ""

def _exception_safe_process_keyboard_commands(tello, fly):
    try:
        return _process_keyboard_commands(tello, fly)
    except Exception as exc:
        LOGGER.error("Error processing keyboard command")
        LOGGER.error(f"{exc}")
        return 1

def _process_keyboard_commands(tello, fly):
    """
    Process keyboard commands via OpenCV.
    :param tello:
    :type tello:
    :param fly: Flag indicating if the Tello is set to fly
    :type bool:
    :return: 0 - Exit, 1 - continue processing, 2 - suspend processing handler
    :rtype:
    """
    global tello_image, battery_update_timestamp, battery_left, last_command, last_command_timestamp

    if tello_image is None:
        tello_image = cv2.imread("./media/tello_drone_image2.png")
        tello_image = imutils.resize(tello_image, width=IMAGE_WIDTH)

    if tello and time.time() - battery_update_timestamp > 10:
        battery_update_timestamp = time.time()
        battery_left = tello.get_battery()

    if time.time() - last_command_timestamp > 2:
        last_command_timestamp = time.time()
        last_command = ""

    exit_flag = 1
    cmd_tello_image = tello_image.copy()
    key = _display_text(cmd_tello_image, last_command, battery_left)

    # because getting keyboard input is a polling process, someone might
    # hold down a key to get the command to register. To avoid getting
    # multiple keyboard commands only look for new commands once the
    # last_command string is empty

    if last_command != "":
        return exit_flag

    if key != 255:
        LOGGER.debug(f"key: {key}")

    if key == 27:  # ESC
        exit_flag = 0

    elif key == ord('w'):
        last_command = "Forward"
        _display_text(cmd_tello_image, last_command, battery_left)
        if fly:
            tello.move_forward(30)

    elif key == ord('s'):
        last_command = "Backward"
        _display_text(cmd_tello_image, last_command, battery_left)
        if fly:
            tello.move_back(30)

    elif key == ord('a'):
        last_command = "Left"
        _display_text(cmd_tello_image, last_command, battery_left)
        if fly:
            tello.move_left(30)

    elif key == ord('d'):
        last_command = "Right"
        _display_text(cmd_tello_image, last_command, battery_left)
        if fly:
            tello.move_right(30)

    elif key == ord('e'):
        last_command = "Clockwise"
        _display_text(cmd_tello_image, last_command, battery_left)
        if fly:
            tello.rotate_clockwise(30)

    elif key == ord('q'):
        last_command = "Counter Clockwise"
        _display_text(cmd_tello_image, last_command, battery_left)
        if fly:
            tello.rotate_counter_clockwise(30)

    elif key == ord('r'):
        last_command = "Up"
        _display_text(cmd_tello_image, last_command, battery_left)
        if fly:
            tello.move_up(30)

    elif key == ord('f'):
        last_command = "Down"
        _display_text(cmd_tello_image, last_command, battery_left)
        if fly:
            tello.move_down(30)

    elif key == ord('l'):
        last_command = "Land"
        _display_text(cmd_tello_image, last_command, battery_left)
        exit_flag = 0

    elif key == ord('h'):
        last_command = "Hover"
        _display_text(cmd_tello_image, last_command, battery_left)
        if fly:
            tello.send_rc_control(0, 0, 0, 0)

    elif key == ord('x'):
        tello.emergency()
        exit_flag = 0  # stop processing the handler function but continue to fly and see video

    # LOGGER.debug(f"Exit Flag: {exit_flag}")
    return exit_flag




def _get_video_frame(frame_read, vid_sim):
    f = None
    try:
        if frame_read:
            f = frame_read.frame
        elif vid_sim and local_video_stream:
            f = local_video_stream.read()

        if f is not None:
            f = imutils.resize(f, width=IMAGE_WIDTH)

    except Exception as exc:
        LOGGER.error("Exception getting video frame")
        LOGGER.error(f"{exc}")

    return f


def process_tello_video_feed(handler_file, video_queue, stop_event, video_event, fly=False, tello_video_sim=False, display_tello_video=False):
    """

    :param exit_event: Multiprocessing Event.  When set, this event indicates that the process should stop.
    :type exit_event:
    :param video_queue: Thread Queue to send the video frame to
    :type video_queue: threading.Queue
    :param stop_event: Thread Event to indicate if this thread function should stop
    :type stop_event: threading.Event
    :param video_event: threading.Event to indicate when the main loop is ready for video
    :type video_event: threading.Event
    :param fly: Flag used to indicate whether the drone should fly.  False is useful when you just want see the video stream.
    :type fly: bool
    :param max_speed_limit: Maximum speed that the drone will send as a command.
    :type max_speed_limit: int
    :return: None
    :rtype:
    """
    global tello, local_video_stream
    last_show_video_queue_put_time = 0
    handler_method = None

    try:
        if fly or ( not tello_video_sim and display_tello_video):
            tello = Tello()
            rtn = tello.connect()
            LOGGER.debug(f"Connect Return: {rtn}")

        if handler_file:
            handler_file = handler_file.replace(".py", "")
            handler_module = importlib.import_module(handler_file)
            init_method = getattr(handler_module, 'init')
            handler_method = getattr(handler_module, 'handler')

            init_method(tello, fly_flag=fly)

        frame_read = None
        if tello and video_queue:
            tello.streamon()
            frame_read = tello.get_frame_read()

        if fly:
            tello.takeoff()
            # send command to go no where
            tello.send_rc_control(0, 0, 0, 0)

        if tello_video_sim and local_video_stream is None:
            local_video_stream = VideoStream(src=0).start()
            time.sleep(2)

        while not stop_event.isSet():
            frame = _get_video_frame(frame_read, tello_video_sim)

            if frame is None:
                # LOGGER.debug("Failed to read video frame")
                if handler_method:
                    handler_method(tello, frame, fly)
                # else:
                #     # stop let keyboard commands take over
                #     if fly:
                #         tello.send_rc_control(0, 0, 0, 0)
                continue

            if handler_method:
                handler_method(tello, frame, fly)
            # else:
            #     # stop let keyboard commands take over
            #     if fly:
            #         tello.send_rc_control(0, 0, 0, 0)

            # send frame to other processes
            if video_queue and video_event.is_set():
                try:
                    if time.time() - last_show_video_queue_put_time > show_video_per_second:
                        last_show_video_queue_put_time = time.time()
                        LOGGER.debug("Put video frame")
                        video_queue.put_nowait(frame)
                except:
                    pass


    except Exception as exc:
        LOGGER.error(f"Exiting Tello Process with exception: {exc}")
        traceback.print_exc()
    finally:
        # then the user has requested that we land and we should not process this thread
        # any longer.
        # to be safe... stop all movement
        if fly:
            tello.send_rc_control(0, 0, 0, 0)

        stop_event.clear()

    LOGGER.info("Leaving User Script Processing Thread.....")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    ap = argparse.ArgumentParser()
    ap.add_argument("--display-video", action='store_true', help="Display Drone video using OpenCV.  Default: 1")
    ap.add_argument("--save-video", action='store_true', help="Save video as MP4 file.  Default: False")
    ap.add_argument("--handler", type=str, required=False, default="",
                    help="Name of the python file with an init and handler method.  Do not include the .py extension and it has to be in the same folder as this main driver")
    output_group = ap.add_mutually_exclusive_group()
    output_group.add_argument('-v', '--verbose', action='store_true', help='Be loud')
    output_group.add_argument('-i', '--info', action='store_true', help='Show only important information')
    fly_sim_group = ap.add_mutually_exclusive_group()
    fly_sim_group.add_argument("--fly", action='store_true',
                               help="Flag to control whether the drone should take flight.  Default: False")
    fly_sim_group.add_argument("--tello-video-sim", action='store_true',
                               help="Flag to control whether to use the computer webcam as a simulated Tello video feed. Default: False")

    args = vars(ap.parse_args())

    LOGGER.setLevel(logging.ERROR)
    if args["verbose"]:
        LOGGER.setLevel(logging.NOTSET)
    if args["info"]:
        LOGGER.setLevel(logging.INFO)

    LOGGER.debug(args.items())

    save_video = args['save_video']
    fly = args['fly']
    LOGGER.debug(f"Fly: {fly}")
    display_video = args['display_video']
    handler_file = args['handler']
    tello_video_sim = args['tello_video_sim']

    # if the user selected tello_video_sim, force the display video flag
    if tello_video_sim:
        display_video = True

    # video queue to hold the frames from the Tello
    video_queue = queue.Queue(maxsize=MAX_VIDEO_Q_DEPTH)


    try:
        # TELLO_LOGGER = logging.getLogger('djitellopy')
        # TELLO_LOGGER.setLevel(logging.ERROR)

        cv2.namedWindow("Tello Video")

        stop_event = threading.Event()
        ready_to_show_video_event = threading.Event()
        p1 = threading.Thread(target=process_tello_video_feed,
                     args=(handler_file, video_queue, stop_event, ready_to_show_video_event, fly, tello_video_sim, display_video,))
        p1.setDaemon(True)
        p1.start()

        while True:
            key_status = _exception_safe_process_keyboard_commands(tello, fly)
            if key_status == 0:
                stop_event.set()
                ready_to_show_video_event.clear()
                # wait up to 5 seconds for the handler thread to exit
                # the handler thread will clear the stop_event when it
                # exits
                for _ in range(5):
                    if stop_event.isSet():
                        time.sleep(1)
                    else:
                        break
                if video_writer:
                    video_writer.release()
                    video_writer = None
                break

            ready_to_show_video_event.set()
            try:
                # LOGGER.debug(f"Q size: {video_queue.qsize()}")
                frame = video_queue.get(block=False)
            except:
                frame = None


            # check for video feed
            if display_video and frame is not None:
                try:
                    # display the frame to the screen
                    cv2.imshow("Tello Video", frame)
                    cv2.waitKey(1)
                except Exception as exc:
                    LOGGER.error(f"Display Queue Error: {exc}")

            # check for save video
            if save_video and frame is not None:
                if video_writer is None:
                    (h, w) = frame.shape[:2]
                    video_file = f"video_{datetime.now().strftime('%d-%m-%Y_%I-%M-%S_%p')}.mp4"
                    video_writer = cv2.VideoWriter(video_file, cv2.VideoWriter_fourcc(*'mp4v'), 10, (w, h), True)

                try:
                    video_writer.write(frame)
                except Exception as exc:
                    LOGGER.error(f"Writing video error: {exc}")
    finally:
        LOGGER.debug("Complete...")

        cv2.destroyWindow("Tello Video")
        cv2.destroyWindow("Keyboard Cmds")
        cv2.destroyAllWindows()
        shutdown_gracefully()
