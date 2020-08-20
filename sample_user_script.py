import time
import logging

"""
Sample user supplied script.  This script will cause the Tello drone to go up and down
and then wait for the TIME_BETWEEN seconds to expire before issuing the next command.

"""
LOGGER = logging.getLogger()

# User Configuration

UP_DOWN_HEIGHT = 30

# Time in seconds
TIME_BETWEEN = 3


def init(tello, fly_flag=False):
    # nothing to initialize
    LOGGER.info("Calling init function of sample_user_script....")


last_command_timestamp = 0
last_command = 'down'


def handler(tello, frame, fly_flag=False):
    global last_command_timestamp, last_command

    if time.time() - last_command_timestamp > TIME_BETWEEN:
        last_command_timestamp = time.time()
        if last_command == 'down':
            last_command = 'up'
            if fly_flag:
                tello.move_up(UP_DOWN_HEIGHT)
        else:
            last_command = 'down'
            if fly_flag:
                tello.move_down(UP_DOWN_HEIGHT)

        LOGGER.debug(f"User Handler Command: {last_command}")









