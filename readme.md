Self driving car using Deep Learning, OpenCv and Python.

Team members: Pritam Mondal, Saikat Dey, Sounak Mondal, Kingshuk Pal.

Hardware used:
Robot Car Chassis
Arduino Uno (for early protoryping)
Raspberry Pi 3b+
Raspi Cam
External battery pack

Aim: To make a robo-car that is capable of lane detection and navigation on a track, and also remote control over the internet.

The client device, i.e. the Raspberry pi mounted on the robo car streams video back to the server, i.e the laptop, for computation.
MQTT protocol is used to communicate with the server.

On the server side, we calculate Region of interest from the streamed images and detect lanes, and decide which way the car should turn.
Then the output is sent to the client.
Multi threading is used in the server script to balance workload and speed up computation.

RPi.GPIO is used to control the motors using Raspberry Pi.

Also, the car can be remotely controlled using the server script.

