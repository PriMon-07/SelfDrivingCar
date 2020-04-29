# Testing
import threading
import cv2 as cv
import numpy as np
import time
import paho.mqtt.client as mqtt
import base64

MQTT_SERVER = "192.168.0.100"
MQTT_RECEIVE = "test_2"
MQTT_SEND = "test_1"

points = [[35, 210], [275, 210], [255, 180], [65, 180]]
points_rap = [(0, 240), (320, 240), (320, 0), (0, 0)]

color_blue = (255, 0, 0)
color_green = (0, 255, 0)
color_red = (0, 0, 255)

frame = frame_pers_lane = frame_thres = frame_thres_final = \
    frame_final_lane = np.zeros((240, 320, 3), np.uint8)

histrogram_lane = histrogram_end = np.zeros(320)

result_lane = result_end = 0


def on_connect(client, usedata, flags, rc):
    print("Connected client1 with result code " + str(rc))
    client.subscribe(MQTT_RECEIVE)


def on_message(client, userdata, msg):
    global frame
    # print(msg.topic+" "+str(msg.payload))
    img = base64.b64decode(msg.payload)
    npimg = np.frombuffer(img, dtype=np.uint8)
    frame = cv.imdecode(npimg, 1)


client1 = mqtt.Client()
client2 = mqtt.Client()
client1.on_connect = on_connect
client1.on_message = on_message
client1.connect(MQTT_SERVER)
client2.connect(MQTT_SERVER)


def nothing(x):
    pass


def point_position():
    global points
    top_width = cv.getTrackbarPos('Top: W', "Tracking") // 2
    top_height = cv.getTrackbarPos('Top: H', "Tracking")
    top_horizontal = cv.getTrackbarPos('Top: Hori', "Tracking")
    down_width = cv.getTrackbarPos('Down: W', "Tracking") // 2
    down_height = cv.getTrackbarPos('Down: H', "Tracking")
    down_horizontal = cv.getTrackbarPos('Down: Hori', "Tracking")

    # Down Points
    mid1 = down_horizontal
    points[0][0] = mid1 - down_width
    points[1][0] = mid1 + down_width

    points[0][1] = down_height
    points[1][1] = down_height

    # Top Points
    mid2 = top_horizontal
    points[3][0] = mid2 - top_width
    points[2][0] = mid2 + top_width

    points[3][1] = top_height
    points[2][1] = top_height


def perspective(original_frame):
    original_frame = cv.circle(original_frame, (points[0][0] - 3, points[0][1] + 3), 4, color_red, cv.FILLED)
    original_frame = cv.circle(original_frame, (points[1][0] + 3, points[1][1] + 3), 4, color_red, cv.FILLED)
    original_frame = cv.circle(original_frame, (points[2][0] + 3, points[2][1] - 3), 4, color_red, cv.FILLED)
    original_frame = cv.circle(original_frame, (points[3][0] - 3, points[3][1] - 3), 4, color_red, cv.FILLED)

    matrix = cv.getPerspectiveTransform(np.float32(points), np.float32(points_rap))
    frame_pers_finished = cv.warpPerspective(original_frame, matrix, (320, 240))
    return frame_pers_finished


def threshold(frame_pers):
    # global frame_gray, frame_thres, frame_edge, frame_final_lane
    frame_gray = cv.cvtColor(frame_pers, cv.COLOR_RGB2GRAY)
    # cv.imshow('gray', frame_gray)
    low = cv.getTrackbarPos('Gray: Low', "Tracking")
    high = cv.getTrackbarPos('Gray: High', "Tracking")
    frame_threshold = cv.inRange(frame_gray, low, high)
    frame_edge = cv.Canny(frame_threshold, 150, 200)
    frame_final = cv.bitwise_or(frame_edge, frame_threshold)
    return frame_threshold, frame_final
    # frame_final = cv.cvtColor(frame_final, cv.COLOR_GRAY2RGB)


def histrogram(frame_final):
    # global histrogram_lane, histrogram_end
    # histro_lane = np.zeros(frame_final.shape[1])
    # histro_end = np.zeros(frame_final.shape[1])
    histro_lane = np.sum(frame_final[frame_final.shape[0] // 2:, :], axis=0)
    histro_end = np.sum(frame_final, axis=0)
    # frame_final = cv.cvtColor(frame_final, cv.COLOR_BGR2GRAY)

    # for i in range(frame_final.shape[1]):
    #     roi_lane = frame_final[160:240, i]
    #     roi_end = frame_final[:, i]
    #     roi_lane = cv.divide(255, roi_lane)
    #     roi_end = cv.divide(255, roi_end)
    #     histro_lane[i] = int(sum(roi_lane))
    #     histro_end[i] = int(sum(roi_end))

    return histro_lane, histro_end


def lane_finder(frame_final, histro_lane, client):
    # global frame_final_lane, result_lane, result_end
    # print(len(frame_final.shape))
    half = int(frame_final.shape[1] / 2)

    l_lane = np.argmax(histro_lane[:half])
    r_lane = np.argmax(histro_lane[half:]) + half

    if r_lane < 170:
        r_lane = 319

    # if l_lane > 150:
    #     l_lane = 1

    lane_center = int((r_lane - l_lane) / 2 + l_lane)
    frame_center = half - 4

    if len(frame_final.shape) == 2:
        frame_final = cv.cvtColor(frame_final, cv.COLOR_GRAY2BGR)

    frame_final = cv.line(frame_final, (l_lane, 240), (l_lane, 0), color_green, 2)
    frame_final = cv.line(frame_final, (r_lane, 240), (r_lane, 0), color_green, 2)

    frame_final = cv.line(frame_final, (lane_center, 240), (lane_center, 0), color_green, 2)
    frame_final = cv.line(frame_final, (frame_center, 240), (frame_center, 0), color_blue, 2)

    result_l = lane_center - frame_center
    result_e = sum(histrogram_end)

    client2.publish(MQTT_SEND, result_l)
    return result_l, result_e, frame_final


def punch(frame_pers):
    frame_threshold, frame_final = threshold(frame_pers)
    histo_lane, histro_end = histrogram(frame_final)
    return frame_threshold, frame_final, histo_lane, histro_end


def on_finished(name_id, a):
    global frame_pers_lane, frame_thres, frame_thres_final, frame_final_lane, \
        histrogram_lane, histrogram_end, result_end, result_lane
    if name_id == "perspective":
        frame_pers_lane = a
    # elif name_id == "thres":
    #     frame_thres = a[0]
    #     frame_final_lane = a[1]
    # elif name_id == "histro":
    #     histrogram_lane = a[0]
    #     histrogram_end = a[1]
    elif name_id == "lane_finder":
        result_lane = a[0]
        result_end = a[1]
        frame_final_lane = a[2]
    elif name_id == "punch":
        frame_thres = a[0]
        frame_thres_final = a[1]
        histrogram_lane = a[2]
        histrogram_end = a[3]


class ThreadPerspective(threading.Thread):
    ex = True

    def __init__(self, name_id, target, on_finish):
        threading.Thread.__init__(self)
        self.threadId = name_id
        self.target = target
        self.on_finish = on_finish
        # self.args = args

    def run(self):
        global frame
        print("Thread Started: " + self.threadId)
        while self.ex:
            arg = (frame, )
            a = self.target(*arg)
            self.on_finish(self.threadId, a)
        print("Thread Finished: " + self.threadId)

    def stop(self):
        self.ex = False


class ThreadPunch(threading.Thread):
    ex = True

    def __init__(self, name_id, target, on_finish):
        threading.Thread.__init__(self)
        self.threadId = name_id
        self.target = target
        self.on_finish = on_finish
        # self.args = args

    def run(self):
        print("Thread Started: " + self.threadId)
        while self.ex:
            arg = (frame_pers_lane, )
            a = self.target(*arg)
            self.on_finish(self.threadId, a)
        print("Thread Finished: " + self.threadId)

    def stop(self):
        self.ex = False


class ThreadLaneFinder(threading.Thread):
    ex = True

    def __init__(self, name_id, target, on_finish):
        threading.Thread.__init__(self)
        self.threadId = name_id
        self.target = target
        self.on_finish = on_finish
        # self.args = args

    def run(self):
        print("Thread Started: " + self.threadId)
        while self.ex:
            arg = (frame_thres_final, histrogram_lane, client2, )
            a = self.target(*arg)
            self.on_finish(self.threadId, a)
        print("Thread Finished: " + self.threadId)

    def stop(self):
        self.ex = False


if __name__ == '__main__':

    cv.namedWindow("Tracking")
    cv.resizeWindow("Tracking", 320, 510)
    cv.createTrackbar("Gray: Low", "Tracking", 0, 255, nothing)
    cv.createTrackbar("Gray: High", "Tracking", 0, 255, nothing)
    cv.createTrackbar("Top: H", "Tracking", 180, 230, nothing)
    cv.createTrackbar("Top: W", "Tracking", 190, 320, nothing)
    cv.createTrackbar("Top: Hori", "Tracking", 160, 320, nothing)
    cv.createTrackbar("Down: H", "Tracking", 210, 240, nothing)
    cv.createTrackbar("Down: W", "Tracking", 240, 320, nothing)
    cv.createTrackbar("Down: Hori", "Tracking", 155, 320, nothing)

    thread_perspective = ThreadPerspective("perspective", perspective, on_finished)
    thread_punch = ThreadPunch("punch", punch, on_finished)
    thread_lane_finder = ThreadLaneFinder("lane_finder", lane_finder, on_finished)

    client1.loop_start()
    thread_perspective.start()
    thread_punch.start()
    thread_lane_finder.start()
    while True:
        point_position()
        cv.putText(frame, str(result_lane), (5, 30), cv.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, color_blue, 2)

        # client2.publish(MQTT_SEND, result_lane)
        cv.imshow('Original', frame)
        cv.imshow('Perspective', frame_pers_lane)
        cv.imshow('Final', frame_final_lane)
        cv.imshow('Threshold', frame_thres)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    client1.loop_stop()
    thread_perspective.stop()
    thread_punch.stop()
    thread_lane_finder.stop()
    cv.destroyAllWindows()
    client1.disconnect()
    client2.disconnect()
    print("Finished Main")