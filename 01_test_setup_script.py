
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
    print(f"Successfully imported cv2 version: {cv2.__version__}")
except:
    print("OpenCV is not installed")
    print_setup_instructions()

try:
    from djitellopy import Tello
    print("Succesfully imported Tello")
except:
    print("DJITelloPy API is not installed")
    print_setup_instructions()

try:
    import imutils
    print("Successfully imported imutils")
except:
    print("imutils is not installed")
    print_setup_instructions()

try:
    import jupyter
    print("Successfully imported jupyter")
except:
    print("jupyter is not installed")
    print_setup_instructions()