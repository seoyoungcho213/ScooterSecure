from machine import SoftI2C, Pin, Timer
from neopixel import NeoPixel
import utime, urequests, network
import mpu6050

# Connect to WiFi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
ssid = 'WRITE YOUR WIFI NAME HERE'
pw = 'WRITE YOUR WIFI PW HERE'
sta_if.connect(ssid, pw)
while not sta_if.isconnected():
    pass
print("Connected to " + ssid)
print("IP Address: " + sta_if.ifconfig()[0])

# Intialization
i2c = SoftI2C(scl=Pin(20), sda=Pin(22))
mpu = mpu6050.accel(i2c)
mpu.get_values()
print("MPU values : ", mpu.get_values())
tim1 = Timer(1)
tim2 = Timer(2)

# Calibration
def calibrate_ms(values):
    return (values['AcX'] * 9.81 / 16384 - 0.343, values['AcY'] * 9.81 / 16384 + 0.101, values['AcZ'] * 9.81 / 16384 + 2.78)

utime.sleep_ms(100)
print('After Calibration (AcX, AcY, AcZ): ', calibrate_ms(mpu.get_values()))

# NeoPixel Initialization
out = Pin(0, Pin.OUT)
np_power = Pin(2, Pin.OUT)
np = NeoPixel(out, 1)
out.value(1)
np_power.value(0)

# IFTTT Initalization
IFTTT_WEBHOOKS_KEY = "PUT YOUR IFTTT WEBHOOKS KEY HERE"
url_notify = "https://maker.ifttt.com/trigger/motion_detected/with/key/" + IFTTT_WEBHOOKS_KEY
MOTION_THRESHOLD = 2.0    # You can adjust motion threshold based on your need

# ThingSpeak Initialization to read data
ACTIVATE = 0
THINGSPEAK_CHANNEL_ID = 'PUT YOUR CHANNEL ID HERE'
THINGSPEAK_READ_API_KEY = 'PUT YOUR READ API KEY HERE'
url_read = "https://api.thingspeak.com/channels/{}/fields/1/last.json?api_key={}".format(
    THINGSPEAK_CHANNEL_ID, THINGSPEAK_READ_API_KEY)

# Send notification to phone
def send_notif():
    response_ifttt = urequests.get(url_notify)
    response_ifttt.close()

def detect_motion(tim2):
    values = calibrate_ms(mpu.get_values())
    result = all(abs(int(value)) > MOTION_THRESHOLD for value in values[:-1])
    if (result == True):
        print("Motion detected!")
        # if MOTION detected, NeoPixel to RED
        np_power.value(1)
        np[0] = (255, 0, 0) 
        np.write()
        send_notif()
        utime.sleep_ms(500)
        np[0] = (0, 255, 0)
        np.write()
    else:
        result = (int(values[-1])) < (-9.8-MOTION_THRESHOLD) or (int(values[-1])) > (-9.8+MOTION_THRESHOLD)
    if (result == True):
        print("Motion detected!")
        # if MOTION detected, NeoPixel to RED
        np_power.value(1)
        np[0] = (255, 0, 0) 
        np.write()
        send_notif()
        utime.sleep_ms(500)
        np[0] = (0, 255, 0)
        np.write()

# if ACTIVATE, NeoPixel to GREEN
cycles = 0
state = 0
def check_actv(tim1):
    global state, cycles
    response = urequests.get(url_read)
    if response.status_code == 200:
        data = response.json()
        ACTIVATE = int(data.get("field1", "N/A"))
        if state != ACTIVATE:
            if ACTIVATE:
                cycles = 0
                np_power.value(1)
                np[0] = (0, 255, 0) # green
                np.write()
                tim2.init(period=1000, mode=Timer.PERIODIC, callback=detect_motion)
            status = ACTIVATE
        if cycles == 3 :
            np_power.value(0)
            tim2.deinit()
        cycles += 1
    else:
        print("ERROR ! Bad Request. HTTP Status Code:", response.status_code)
        return

check_actv(None)
# check ThingSpeak every 30s
tim1.init(period=30000, mode=Timer.PERIODIC, callback=check_actv)
