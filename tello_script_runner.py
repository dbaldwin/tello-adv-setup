import cv2
from djitellopy import Tello
import signal
import sys
import time
from datetime import datetime
from multiprocessing import Manager, Process, Queue
import argparse
import importlib
import logging
from imutils.video import VideoStream
import imutils

FORMAT = '%(asctime)-15s %(levelname)-10s %(message)s'
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger()

tello = None
video_writer = None

# This is hard coded because if the image gets too big then
# the lag in the video stream gets very pronounced.  This is
# parameter that will be system configured and the user will
# not be allowed change it at run time
IMAGE_WIDTH = 500

# function to handle keyboard interrupt
def signal_handler(sig, frame):
    global video_writer
    print(f"Signal Handler: {frame}")
    if tello:
        try:
            tello.streamoff()
            tello.land()
        except:
            pass

    if video_writer:
        try:
            video_writer.release()
            video_writer = None
        except:
            pass

    sys.exit()


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

def _exception_save_process_keyboard_commands(tello, fly):
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
        if fly:
            tello.land()
        exit_flag = 0

    elif key == ord('x'):
        exit_flag = 2  # stop processing the handler function but continue to fly and see video

    # LOGGER.debug(f"Exit Flag: {exit_flag}")
    return exit_flag


local_video_stream = None


def _get_video_frame(frame_read, vid_sim):
    global local_video_stream
    try:
        if vid_sim and local_video_stream is None:
            local_video_stream = VideoStream(src=0).start()
            time.sleep(2)

        if frame_read:
            f = frame_read.frame
            f = imutils.resize(f, width=IMAGE_WIDTH)
            return f
        elif vid_sim and local_video_stream:
            f = local_video_stream.read()
            f = imutils.resize(f, width=IMAGE_WIDTH)
            return f

    except Exception as exc:
        LOGGER.error("Exception getting video frame")
        LOGGER.error(f"{exc}")

    return None


def process_tello_video_feed(handler_file, show_video_queue, video_writer_queue, fly=False, tello_video_sim=False):
    """

    :param exit_event: Multiprocessing Event.  When set, this event indicates that the process should stop.
    :type exit_event:
    :param show_video_queue: Pipe to send video frames to the process that will show the video
    :type show_video_queue: multiprocessing Pipe
    :param video_writer_queue: Pipe to send video frames to the process that will save the video frames
    :type video_writer_queue: multiprocessing Pipe
    :param fly: Flag used to indicate whether the drone should fly.  False is useful when you just want see the video stream.
    :type fly: bool
    :param max_speed_limit: Maximum speed that the drone will send as a command.
    :type max_speed_limit: int
    :return: None
    :rtype:
    """
    global tello
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    handler_method = None

    try:
        if fly or ( not tello_video_sim and (show_video_queue or video_writer_queue)):
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
        if tello and (show_video_queue or video_writer_queue):
            tello.streamon()
            time.sleep(2)
            frame_read = tello.get_frame_read()

        if fly:
            tello.takeoff()

        processing_flag = _exception_save_process_keyboard_commands(tello, fly)
        while processing_flag != 0:
            frame = _get_video_frame(frame_read, tello_video_sim)

            if frame is None:
                # print("Failed to read video frame")
                if handler_method and processing_flag == 1:
                    handler_method(tello, frame, fly)
                else:
                    # stop let keyboard commands take over
                    if fly:
                        tello.send_rc_control(0, 0, 0, 0)
                processing_flag = _exception_save_process_keyboard_commands(tello, fly)
                continue

            if handler_method and processing_flag == 1:
                handler_method(tello, frame, fly)
            else:
                # stop let keyboard commands take over
                if fly:
                    tello.send_rc_control(0, 0, 0, 0)

            # send frame to other processes
            if show_video_queue:
                show_video_queue.put(frame)

            if video_writer_queue:
                video_writer_queue.put(frame)

            processing_flag = _exception_save_process_keyboard_commands(tello, fly)
            if processing_flag == 2:
                # then stop processing the handler
                # assume something is wrong in the handler code
                handler_method = None
    except Exception as exc:
        LOGGER.error(f"Exiting Tello Process with exception: {exc}")

    finally:
        # then we got the exit event so cleanup
        signal_handler(None, "Tello Process")


def show_video(frame_queue):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    LOGGER.debug("Start Show Video Process")

    while True:
        try:
            frame = frame_queue.get()
            # display the frame to the screen
            cv2.imshow("Tello Video", frame)
            cv2.waitKey(1)
        except Exception as exc:
            LOGGER.error(exc)


def video_recorder(frame_queue, height=375, width=IMAGE_WIDTH):
    global video_writer
    # create a VideoWrite object, recoring to ./video.avi
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    LOGGER.debug("Start Video Recorder")

    if video_writer is None:
        video_file = f"video_{datetime.now().strftime('%d-%m-%Y_%I-%M-%S_%p')}.mp4"
        video_writer = cv2.VideoWriter(video_file, cv2.VideoWriter_fourcc(*'mp4v'), 30, (width, height))

    while True:
        frame = frame_queue.get()
        video_writer.write(frame)
        # time.sleep(1 / 15)

    # then we got the exit event so cleanup
    signal_handler(None, "Video Writer")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    LOGGER.info("****************")
    LOGGER.info("execute: export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES  ")
    LOGGER.info("****************")

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

    display_video_queue = None
    if display_video:
        display_video_queue = Queue()

    save_video_queue = None
    if save_video:
        save_video_queue = Queue()

    with Manager() as manager:
        p1 = Process(target=process_tello_video_feed,
                     args=(handler_file, display_video_queue, save_video_queue, fly, tello_video_sim))

        if display_video:
            p2 = Process(target=show_video, args=(display_video_queue,))
        else:
            p2 = None

        if save_video:
            p3 = Process(target=video_recorder, args=(save_video_queue,))
        else:
            p3 = None

        if p2:
            p2.start()

        if p3:
            p3.start()

        p1.start()

        p1.join()
        if p2:
            p2.terminate()

        if p3:
            p3.terminate()

        if p2:
            p2.join()

        if p3:
            p3.join()

    cv2.destroyAllWindows()
    LOGGER.info("Complete...")
