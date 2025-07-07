from importlib import import_module
import os
from flask import Flask, render_template, Response, request
import RPi.GPIO as GPIO

from camera_pi2 import Camera


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


def cleanup_gpio():
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()


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

def turn_left():
    pwm_left.ChangeDutyCycle(60)
    pwm_right.ChangeDutyCycle(80)
    GPIO.output(Motor_B_Pin1, GPIO.HIGH)
    GPIO.output(Motor_B_Pin2, GPIO.LOW)
    GPIO.output(Motor_A_Pin1, GPIO.LOW)
    GPIO.output(Motor_A_Pin2, GPIO.HIGH)

def turn_right():
    pwm_left.ChangeDutyCycle(80)
    pwm_right.ChangeDutyCycle(60)
    GPIO.output(Motor_B_Pin1, GPIO.LOW)
    GPIO.output(Motor_B_Pin2, GPIO.HIGH)
    GPIO.output(Motor_A_Pin1, GPIO.HIGH)
    GPIO.output(Motor_A_Pin2, GPIO.LOW)

def stop_motors():
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(0)
    GPIO.output(Motor_B_Pin1, GPIO.LOW)
    GPIO.output(Motor_B_Pin2, GPIO.LOW)
    GPIO.output(Motor_A_Pin1, GPIO.LOW)
    GPIO.output(Motor_A_Pin2, GPIO.LOW)


app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control', methods=['POST'])
def control():
    command = request.form.get('command')
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
    return '', 204



if __name__ == '__main__':
    try:
        print("HI")
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        cleanup_gpio()
