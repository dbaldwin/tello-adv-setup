
# Test that the necessary imports and libraries are available
def print_setup_instructions():
    print("Make sure your python virtual environment is activated")
    print("Open a Terminal window (MacOS) or Command Prompt (Windows) and run:")
    print("""
    pip install -r requirements.txt
    pip install https://github.com/damiafuentes/DJITelloPy/archive/master.zip
    """)

try:
    import cv2
except:
    print("OpenCV is not installed")
    print_setup_instructions()

try:
    from djitellopy import Tello
except:
    print("DJITelloPy API is not installed")
    print_setup_instructions()

try:
    import imutils
except:
    print("imutils is not installed")
    print_setup_instructions()
