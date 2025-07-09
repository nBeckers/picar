#!/usr/bin/env/python
# File name   : LedClient.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/03/22

import socket
import sys
import threading
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from importlib import import_module
import os
import RPi.GPIO as GPIO
from board import SCL, SDA
import busio

# from camera_pi2 import Camera
from picamera2 import Picamera2, Preview
import cv2
import time
from datetime import datetime

# GPIO setup
Motor_A_EN = 4
Motor_B_EN = 17
Motor_A_Pin1 = 26
Motor_A_Pin2 = 21
Motor_B_Pin1 = 27
Motor_B_Pin2 = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(Motor_A_EN, GPIO.OUT)
GPIO.setup(Motor_B_EN, GPIO.OUT)
GPIO.setup(Motor_A_Pin1, GPIO.OUT)
GPIO.setup(Motor_A_Pin2, GPIO.OUT)
GPIO.setup(Motor_B_Pin1, GPIO.OUT)
GPIO.setup(Motor_B_Pin2, GPIO.OUT)

pwm_left = GPIO.PWM(Motor_B_EN, 1000)
pwm_right = GPIO.PWM(Motor_A_EN, 1000)
pwm_left.start(0)
pwm_right.start(0)

i2c = busio.I2C(SCL, SDA)
pwm_servo = PCA9685(i2c, address=0x40)
pwm_servo.frequency = 50

servos = [servo.Servo(
    pwm_servo.channels[i],
    min_pulse=500,
    max_pulse=2400) for i in range(5)]

should_exit = False



def cleanup_gpio():
    pwm_servo.deinit()
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()


def set_servo_angle(channel, angle):
    if 0 <= angle <= 180:
        servos[channel].angle = angle
    else:
        print("Angle must be between 0 and 180 degrees.")

    time.sleep(2)


# Movement functions
def move_forward():
    pwm_left.ChangeDutyCycle(100)
    pwm_right.ChangeDutyCycle(100)
    GPIO.output(Motor_B_Pin1, GPIO.HIGH)
    GPIO.output(Motor_B_Pin2, GPIO.LOW)
    GPIO.output(Motor_A_Pin1, GPIO.HIGH)
    GPIO.output(Motor_A_Pin2, GPIO.LOW)


def move_backward():
    pwm_left.ChangeDutyCycle(100)
    pwm_right.ChangeDutyCycle(100)
    GPIO.output(Motor_B_Pin1, GPIO.LOW)
    GPIO.output(Motor_B_Pin2, GPIO.HIGH)
    GPIO.output(Motor_A_Pin1, GPIO.LOW)
    GPIO.output(Motor_A_Pin2, GPIO.HIGH)


def no_turn():
    set_servo_angle(0, 90)


def turn_left():
    set_servo_angle(1, 135)
    '''
    pwm_left.ChangeDutyCycle(60)
    pwm_right.ChangeDutyCycle(80)
    GPIO.output(Motor_B_Pin1, GPIO.HIGH)
    GPIO.output(Motor_B_Pin2, GPIO.LOW)
    GPIO.output(Motor_A_Pin1, GPIO.LOW)
    GPIO.output(Motor_A_Pin2, GPIO.HIGH)
    '''


def turn_right():
    set_servo_angle(0, 45)
    '''
    pwm_left.ChangeDutyCycle(80)
    pwm_right.ChangeDutyCycle(60)
    GPIO.output(Motor_B_Pin1, GPIO.LOW)
    GPIO.output(Motor_B_Pin2, GPIO.HIGH)
    GPIO.output(Motor_A_Pin1, GPIO.HIGH)
    GPIO.output(Motor_A_Pin2, GPIO.LOW)
    '''


def stop_motors():
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(0)
    GPIO.output(Motor_B_Pin1, GPIO.LOW)
    GPIO.output(Motor_B_Pin2, GPIO.LOW)
    GPIO.output(Motor_A_Pin1, GPIO.LOW)
    GPIO.output(Motor_A_Pin2, GPIO.LOW)




def receive_message(client_socket):
    global should_exit
    while not should_exit:
        try:
            client_socket.settimeout(1)
            data = client_socket.recv(1024)
            if data:
                message = data.decode('utf-8')
                handle_command(message)
                print(f"Received from server: {message}")
            else:
                break
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Error receiving message: {e}")
            break




def handle_command(command):

    if command == 'forward':
        move_forward()
    elif command == 'backward':
        move_backward()
    elif command == 'left':
        turn_left()
    elif command == 'right':
        turn_right()
    elif command == 'stop':
        stop_motors()
    elif command == 'no_turn':
        no_turn()



picam2 = Picamera2()
time.sleep(1)
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()
time.sleep(2)



if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Please enter the server's IP address when running, for example: python3 client.py 192.168.1.31")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = 8000

    # Create a TCP - based socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((server_ip, server_port))
        receive_thread = threading.Thread(target=receive_message, args=(client_socket,))
        receive_thread.start()
        while True:
            # Get input from the keyboard
            message = input("Please enter the message to send (type 'exit' to quit): ")
            if message.lower() == 'exit':
                break
            # Send the message to the server
            client_socket.send(message.encode('utf-8'))
    except socket.error as e:
        print(f"Error connecting to the server: {e}")
    finally:
        cleanup_gpio()
        client_socket.close()
        if 'receive_thread' in locals():
            receive_thread.join()

    
