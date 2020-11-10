# Tello Python Development Setup Tutorial

## Introduction

The purpose of this tutorial is to provide instructions and test cases to make sure your development environment is ready for advanced Python development with the Tello Drone.

This tutorial will make sure the following is ready to go:

> Python 3.6 or greater is installed on your machine

> Create a Python virtual environment

> Activate a Python virtual environment

> Install the necessary Python packages
> * Jupyter
> * PyTello
> * imutils
> * OpenCV

> Start Jupyter Notebook

> Control the Tello using a Jupyter Notebook

> Use a Python script to verify the Tello streaming video

## Verify Python Installation

For the advanced Python Tello programming tutorials and courses it will be assumed that you have installed Python 3.6 or greater.  Python 3.6, 3.7, 3.8 are all acceptable versions of Python.

This tutorial will not go through how to install Python as this is covered in the "Tello Drone Programming with Python - Video Course"

To verify that python is installed and we have access to the right version, open a terminal window on MacOS or a Cmd window on Microsoft Windows.

Type the following:

`python3 --version`

You should see something like:

`python 3.7.7`

or

`python 3.6.6`

or

`python 3.8.3`

If you received a message like:

`command not found`

This means you do not have python3 installed and I encourage you to enroll in the [OpenCV, Python, and DroneBlocks for Tello Camera Control](https://learn.droneblocks.io/p/opencv-python-and-droneblocks-for-tello-camera-control) course.

Alternatively you can download and install from the [Python.org site](https://www.python.org/downloads/).  Select your operating system and follow the instructions.

## Github Code and Creating a Python Virtual Environment

What is a Python Virtual Environment?

When you installed Python and went to the command line and typed, `python3 --version`, that checked the global Python environment.  Unless you have a local environment, which we will learn how to setup shortly, all interactions with Python are through the global environment.

However, when you work on multiple Python projects, you want each project to use its own copy of the Python environment.  This way any changes made in the project, wont impact any other project.  To do that we create a local Python Virtual Environment for every project we create.

We are going to creae a tello_projects diretory, or folder, to hold all of our projects.  We are then going to create a directory called, `tello_setup` inside the `tello_projects` directory.

Let us see how to do that.

* Open a new terminal or cmd window

* Create a directory called `tello_projects'
>       `mkdir tello_projects`

* Change directory into `tello_projects`
>       `cd tello_projects`

Once we have created tello_projects, and we are in the `tello_projects` directory we are now ready get the code from Github.

In a browser go to the url:

```text
https://www.github.com/dbaldwin/tello-adv-setup
```

From that page your there will be a `CODE` button where you can either download a zip file or get the `git clone` url.

Make sure you clone or unzip the file into the `tello_projects` directory.

There are a number of ways to create a Python virtual environment.  I am going to show you one way to do this but if you research other ways it is perfectly acceptable for you to use any method you are comfortable with.

In the terminal/cmd window continue with the following instructions.

* Type the following command:
>       `python3 -m venv venv`

This will instruct Python3 to create a virtual, Python3 environment that looks just like the global version, and put this in a new directory called `.venv`

## Activate a Python virtual environment

To use this environment in the window type the following in the terminal/cmd window:

MacOS:
>       `source .venv/bin/activate`

Windows:
>       `.\venv\Scripts\activate`

At this point you now have a Python virtual environment for the `tello_setup` project that is not shared with any other project, and we have activated it in the current terminal window.

Keep in mind that the environment is only active in the current terminal window.

If you would like to create a new terminal window, and activate the `tello_setup` virtual environment you would perform the following:

* Open a new terminal/cmd window

```shell script
cd tello_projects/tello_setup
source .venv/bin/activate
```
## Install OpenCV

The installation of OpenCV is covered in the course, [OpenCV, Python, and DroneBlocks for Tello Camera Control](https://learn.droneblocks.io/p/opencv-python-and-droneblocks-for-tello-camera-control) . If you do not have OpenCV installed please refer to that course for instructions on how to install OpenCV

In your terminal/cmd window type the following:

```shell script
pip install opencv-python
pip install opencv-contrib-python

```

### Verify OpenCV 4.x is Installed

To verify that OpenCV is installed, open a terminal window or cmd window.

Type the following:

`python`

This will open a Python interpreter and it will look something like the following:
```shell script
Python 3.7.7 (default, Mar 10 2020, 15:43:03)
[Clang 11.0.0 (clang-1100.0.33.17)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>>
```
At the '>>>' type the following:

`import cv2` and press return

If you do not have OpenCV installed you should see something like the following:

```shell script
>>> import cv2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ModuleNotFoundError: No module named 'cv2'
```
if you do not see an error message, type the following:

`cv2.__version__` and press return.

You should see something like the following:
```shell script
Python 3.7.7 (default, Mar 10 2020, 15:43:03)
[Clang 11.0.0 (clang-1100.0.33.17)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import cv2
>>> cv2.__version__
'4.2.0'
>>>
```
If you do not see the version string such as, '4.2.0', or '4.3.0' then please see the course for how to install OpenCV.

To verify that the OpenCV contributor packages were installed type the following:

`import cv2.aruco` and press return

You should see no errors.

```shell script
Python 3.7.7 (default, Mar 10 2020, 15:43:03)
[Clang 11.0.0 (clang-1100.0.33.17)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import cv2
>>> cv2.__version__
'4.2.0'
>>> import cv2.aruco
>>>
```


## Install the necessary Python packages

With our project directory created, and our Python virtual envionment created and activated, we are now ready to start to install the necessary Python packages.

We are going to install 2 packages:

* Jupyter

* DJITelloPy

### Install Jupyter Notebook

As described in the course, "Tello Drone Programming with Python - Video Course" a Jupyter Notebook is a way to run Python in a web browser.

In the terminal/cmd window type:

`pip install jupyter`

### DJITelloPy

The course, "Tello Drone Programming with Python - Video Course" talked about how to communicate from a Python program to the Tello drone using Sockets, IP Addresses and UDP messages.  In that course we saw how to directly interact with the Tello, and how to handle errors and retries.  Instead of building out the Tello API we are going to use an OpenSource Tello API that has already been created, tested and makes interfacing with the Tello much easier.

The Github repository can be found here: https://github.com/damiafuentes/DJITelloPy

To install the DJITelloPy API package, in the terminal window type the following:

`pip install https://github.com/damiafuentes/DJITelloPy/archive/master.zip`

When the pip command completes let us check that the install worked.

In the terminal window type the following:

```shell script
python
from djitellopy import Tello
```

If everything worked you should see:
```shell script
(.venv) Patricks-MacBook-Pro:tello_setup patrickryan$ python
Python 3.7.7 (default, Mar 10 2020, 15:43:03)
[Clang 11.0.0 (clang-1100.0.33.17)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from djitellopy import Tello
>>>
```

## Start Jupyter Notebook

In the terminal/cmd window type:

`jupyter notebook`

After the browser opens, select the notebook named: `Tello_Setup_Test_Notebook`

## Control the Tello through Jupyter Notebook

As described in a previous course, a Jupyter Notebook is made up of two kinds of cells:

* Text Cell

* Code Cell

To execute the Code Cells you can select the cell and press the run button at the top or press ctrl - enter.

Read the instructions and run the cells one by one.


## Verify the OpenCV Video Stream 

In this section we are going to get used to running Python scripts on the command line.  In future courses we will use both Jupyter Notebooks and Python scripts.

Make sure you have a terminal or cmd window open.  You have changed directory to the tello_setup project directory and have activated the Python environment.

Open the script `tello_camera_no_fly.py`

Let's look at the contents of this script.

```python
from djitellopy import Tello
import cv2
```

We are importing our Tello package and the CV2 library

```python
# Create Tello Object
tello = Tello()

# Connect to Tello
tello.connect()

# Start the video Stream
tello.streamon()

# Get the frame reader
frame_reader = tello.get_frame_read()
```

In this section we are creating the Tello object, connecting to the Tello drone.  Recall the `connect` method sends the `command` command.  Next, initialize the video stream and get the frame reader.

```python

while True:
    # In reality you want to display frames in a seperate thread. Otherwise
    #  they will freeze while the drone moves.

    # Read a video frame from Tello
    img = frame_reader.frame

    # Have OpenCV display the Video Frame
    cv2.imshow("drone", img)

    # If ESC is pressed then stop
    key = cv2.waitKey(1) & 0xff
    if key == 27: # ESC
        break

```

In this section, we entry an infinite `while` loop, and you have to be careful with inifinite loops.

In this loop, we use the `frame_reader` to retrieve a video frame.  We then use OpenCV to show the image in a new window with the `cv2.imshow` function call.

Next we have OpenCV look for keyboard input.  If the the ESC key is pressed, then the loop will exit.  The the ESC key is not pressed, then the loop will start over retrieving another video frame.

```python
cv2.destroyWindow('drone')
cv2.destroyAllWindows()
tello.streamoff()
```

When the loop exits, we will clean up the window showing the video by calling `destroyWindow`.  Next we call `destroyAllWindows.  While not strictly required in this case, it is considered good practice.

Last we turn the video stream off on the Tello.

### Lets run the script

* Power on the Tello drone

* Connect to the Tello WIFI access point

* In the terminal window type the following:

```text
python tello_camera_no_fly.py
```

After a few moments you should see the OpenCV window open and be able to view the video feed from the Tello.

To exit this script, press `ctrl-c` in the terminal/cmd window.

## Script to control the Tello and view Video Stream

This script is similar to the previous script, except this time we are going to allow the Tello to take off and control the Tello with keyboard commands.

This is just a test script and in the future will use separate Threads to control the Tello and view the Video stream.

Here are the keyboard commands for controlling the Tello once the video is displaying:

* w: move forward

* s: move backwards

* a: move left

* d: move right

* r: move up

* d: move down

* e: rotate clockwise

* q: rotate counter-clockwise

* l: land

Make sure the Tello is powered on, and you are connected to the Tello WIFI access point.

in a terminal/cmd window type:

```text
python tello_camera_fly.py
```

After a few seconds you should see a window open up showing the video stream.  Select the window to make it the active window and you can now issue keyboard commands.

## DroneBlocks Tello Script Runner

In this last section we are going to cover a script that we will use in many of the advanced Tello programming courses.

The script is, `tello_script_runner.py`

Before executing the `tello_script_runner.py` script, if you are on MacOS you must export a variable in the terminal window.

The `tello_script_runner.py` script will create processes to execute capability such as viewing the video feed.  In a recent update to MacOS, Apple by default does not allow a Python program to fork additional processes.  This is a security feature to keep malicious programs from doing bad things, but it also keeps our program from doing good things!

To inform MacOS that it is ok to allow us to run the `tello_script_runner.py`, in a terminal window type the following:

```text
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```
This will not impact your system and it is only valid for the terminal window you executed it in.



## Conclusion

Congratulations!  You have successfully completed this tutorial and verified that your development environment is ready to build advanced Tello programming with Python.

I hope you are excited to learn advanced Python programming for the Tello and how to apply computer vision.
