# User Configuration
SAMPLE_CONFIG_ITEM = 42


def init(tello, fly_flag=False):
    """

    :param tello: Reference to the DJITelloPy Tello object.
    :type tello: Tello
    :param fly_flag: True - the fly flag was specified and the Tello will take off. False - the Tello will NOT
                        be instructed to take off
    :type fly_flag:  bool
    :return: None
    :rtype:
    """
    print(f"Inside init method.  fly_flag: {fly_flag}, sample config item: {SAMPLE_CONFIG_ITEM}")


def handler(tello, frame, fly_flag=False):
    """

    :param tello: Reference to the DJITelloPy Tello object.
    :type tello: Tello
    :param frame: image
    :type frame:
    :param fly_flag: True - the fly flag was specified and the Tello will take off. False - the Tello will NOT
                        be instructed to take off
    :type fly_flag:  bool
    :return: None
    :rtype:
    """
    print(f"Inside handler method.  fly_flag: {fly_flag}, sample config item: {SAMPLE_CONFIG_ITEM}")
