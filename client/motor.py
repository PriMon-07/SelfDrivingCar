import RPi.GPIO as GPIO
import time

enA = 26
in1 = 19
in2 = 13
in3 = 16
in4 = 20
enB = 21
left_pwm = None
righ_pwm = None


def pin_setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(in1, GPIO.OUT)
    GPIO.setup(in2, GPIO.OUT)
    GPIO.setup(enA, GPIO.OUT)
    GPIO.setup(in3, GPIO.OUT)
    GPIO.setup(in4, GPIO.OUT)
    GPIO.setup(enB, GPIO.OUT)


def pin_activate():
    global left_pwm, righ_pwm
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)
    left_pwm = GPIO.PWM(enA, 2000)
    righ_pwm = GPIO.PWM(enB, 2000)
    left_pwm.start(25)
    righ_pwm.start(25)


def forward():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(15)
    righ_pwm.ChangeDutyCycle(15)


# time.sleep(.3)
# stop()
# time.sleep(1)


def backward():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)
    left_pwm.ChangeDutyCycle(25)
    righ_pwm.ChangeDutyCycle(25)


def left_low():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(25)
    righ_pwm.ChangeDutyCycle(30)
    time.sleep(.1)
    stop()
    time.sleep(.2)


def left_mid():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(25)
    righ_pwm.ChangeDutyCycle(35)
    time.sleep(.2)
    stop()
    time.sleep(.5)


def left_high():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(15)
    righ_pwm.ChangeDutyCycle(35)
    time.sleep(.2)
    stop()
    time.sleep(1)


def right_low():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(30)
    righ_pwm.ChangeDutyCycle(25)
    time.sleep(.1)
    stop()
    time.sleep(.2)


def right_mid():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(35)
    righ_pwm.ChangeDutyCycle(25)
    time.sleep(.2)
    stop()
    time.sleep(.5)


def right_high():
    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.HIGH)
    GPIO.output(in4, GPIO.LOW)
    left_pwm.ChangeDutyCycle(35)
    righ_pwm.ChangeDutyCycle(15)
    time.sleep(.2)
    stop()
    time.sleep(.5)


def stop():
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)


def cleanup():
    GPIO.cleanup()

# pin_setup()
# pin_activate()

# try:
# 	while True:
# 		forward()
# except:
# 	# backward()
# 	# # left_pwm.ChangeDutyCycle(15)
# 	# # righ_pwm.ChangeDutyCycle(15)
# 	# time.sleep(5)
# 	cleanup()
