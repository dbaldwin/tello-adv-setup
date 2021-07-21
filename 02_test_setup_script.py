from djitellopy import Tello
import time

print("**************************")
print("Make sure you are connected to the Tello Drone WiFi Network")
print("**************************")

tello = Tello()

tello.connect()
time.sleep(2)

response = tello.get_battery()
print(response)
time.sleep(2)

tello.takeoff()
time.sleep(2)

tello.move_up(40)
time.sleep(2)

tello.move_down(40)
time.sleep(2)


# Create a loop to go up and down 3 times
# range(0,4) - produces the numbers 0,1,2,3.  It is said to be exclusive of the last number 4.
print(f"Height: {tello.get_height()}")
for i in range(0,4):
    print("Move Up")
    tello.move_up(40)
    print(f"Height: {tello.get_height()}")
    print("Move Down")
    tello.move_down(40)
    print(f"Height: {tello.get_height()}")
time.sleep(2)


tello.move_left(30)
time.sleep(2)

tello.move_back(30)
time.sleep(2)

tello.rotate_clockwise(180)
time.sleep(2)

tello.rotate_counter_clockwise(180)
time.sleep(2)

result = tello.get_battery()
print(result)
time.sleep(2)

result=tello.get_flight_time()
print(result)
time.sleep(2)

result=tello.get_temperature()
print(result)
time.sleep(2)


tello.land()

