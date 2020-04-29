import paho.mqtt.client as mqtt
import time
import cv2 as cv
import base64
import threading
import client.motor as motor

MQTT_SERVER = "192.168.0.100"
MQTT_RECEIVE = "test_1"
MQTT_SEND = "test_2"

cap = cv.VideoCapture(0)
result = -100


def frame_setup():
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv.CAP_PROP_FPS, 15)
    print(cap.isOpened())


def direction(result_lane):
    if -5 < result_lane < 5:
        motor.forward()
        print("Forward")

    elif 5 <= result_lane < 10:
        motor.right_low()
        print("Right1")

    elif 10 <= result_lane < 25:
        motor.right_mid()
        print("Right2")

    elif 25 <= result_lane < 60:
        motor.right_high()
        print("Right3")

    elif -5 >= result_lane > -10:
        motor.left_low()
        print("Left1")

    elif -10 >= result_lane > -25:
        motor.left_mid()
        print("Left2")

    elif -25 >= result_lane > -60:
        motor.left_high()
        print("Left3")

    else:
        motor.stop()
        print("St")


def on_connect1(client, userdata, flags, rc):
    print("Connected client1 with result code " + str(rc))
    client.subscribe(MQTT_RECEIVE)


def on_connect2(client, userdata, flags, rc):
    print("Connected client2 with result code " + str(rc))
    # client.subscribe(MQTT_SEND)


def on_message(client, userdata, msg):
    global result
    # print(msg.topic+" "+str(msg.payload))
    result = int(msg.payload)
    print(result)
    # direction(result)


class ThreadMotor(threading.Thread):
    ex = False

    def __init__(self, name_id):
        threading.Thread.__init__(self)
        self.threadId = name_id
        # self.args = args

    def run(self):
        while True:
            arg = result
            # time.sleep(.5)
            direction(arg)
            if self.ex:
                print("Thread Finished: " + self.threadId)
                break

    def stop(self):
        self.ex = True


client1 = mqtt.Client()
client2 = mqtt.Client()
client1.on_connect = on_connect1
# client2.on_connect = on_connect2
client1.on_message = on_message
client1.connect(MQTT_SERVER)
client2.connect(MQTT_SERVER)

thread_motor = ThreadMotor("Motor")

motor.pin_setup()
motor.pin_activate()
frame_setup()
_, frame = cap.read()
print(frame.shape)
client1.loop_start()
thread_motor.start()

# while True:
#     _, frame = cap.read()
#     encoded, buffer = cv.imencode('.jpg', frame)
#     jpg_as_text = base64.b64encode(buffer)
#     client2.publish(MQTT_SEND, jpg_as_text)
#     client1.loop()

try:
    while True:
        start = time.time()
        _, frame = cap.read()
        encoded, buffer = cv.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        client2.publish(MQTT_SEND, jpg_as_text)
        end = time.time()
        # client1.loop()
        end = time.time()
        t = end - start
        fps = 1 / t
        print(fps)
except:
    cap.release()
    client1.loop_stop()
    client1.disconnect()
    client2.disconnect()
    thread_motor.stop()
    if thread_motor.is_alive():
        thread_motor.join()
    motor.cleanup()
    print("\nNow you can restart fresh")
