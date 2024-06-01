# ScooterSecure

This project is made to prevent stealing using ESP32. It can send notification to user's phone whenever motion is detected. This is intended to attach it your electric scooter or valueables.

'mpu6050.py' is used to get the three-dimensional location data (x, y, z).

'motion_detect.py' is the main file for detecting the motion and sending a notification. It also includes features like connecting to internet and integrating IoT (Thingspaeak) using socket APIs and HTTP.

Hardware used:
  ESP32 Feather V2 (https://www.adafruit.com/product/5400)

Software used:
  Python
  IoT (ThinkSpeak)
  IFTTT
