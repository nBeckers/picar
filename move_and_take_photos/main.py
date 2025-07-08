from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from importlib import import_module
import os
from flask import Flask, render_template, Response, request, send_from_directory
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

def cleanup_gpio():
    pwm_servo.deinit()
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()



def set_servo_angle(channel, angle):
    
    servo_angle = servo.Servo(
        pwm_servo.channels[channel],
        min_pulse=500,
        max_pulse=2400,
        actuation_range=180
    )
    servo_angle.angle = angle
    

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


app = Flask(__name__)
picam2 = Picamera2()
time.sleep(1)
picam2.configure(picam2.create_video_configuration(main={"size":(640, 480)}))
picam2.start()
time.sleep(2)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')



@app.route('/take_photo')
def take_photo():
    # Create a unique filename based on timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"photo_{timestamp}.jpg"
    filepath = os.path.join("./photos", filename)
    
    # Capture and save the image
    picam2.capture_file(filepath)
    
    # Return the image file to the user
    return send_from_directory("./photos", filename, as_attachment=True, download_name=filename)


def gen_frames():
    
    """Video streaming generator function."""
    
    while True:
        frame = picam2.capture_array()
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(),
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
    elif command == 'no_turn':
        no_turn()
    return '', 204



if __name__ == '__main__':
    try:
        os.makedirs("./photos", exist_ok=True)
        app.run(debug=False, host='0.0.0.0', port=5000)
    finally:
        cleanup_gpio()
