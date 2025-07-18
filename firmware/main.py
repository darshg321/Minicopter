from machine import Pin, PWM, I2C, ADC
import time
from MPU6050 import MPU6050

# pwm
motor_pins = [18, 17, 3, 4]
motors = [PWM(Pin(p), freq=20000, duty_u16=0) for p in motor_pins]

def set_throttle(percent: int):
    duty = int((percent / 100) * 65535)
    for m in motors:
        m.duty_u16(duty)

adc_battery = ADC(Pin(15))
adc_battery.atten(ADC.ATTN_11DB)  # full 0-3.3V range

def read_battery_voltage():
    raw = adc_battery.read()
    voltage = (raw / 4095) * 3.3 * 2  # voltage divider
    return voltage

# i2c gy-87 sensors
i2c = I2C(0, scl=Pin(8), sda=Pin(7))
time.sleep(1)

mpu = MPU6050(i2c)

# basic pid
target_pitch = 0
Kp = 1.0
Ki = 0.0
Kd = 0.0
last_error = 0
integral = 0

def pid(current_pitch):
    global last_error, integral
    error = target_pitch - current_pitch
    integral += error
    derivative = error - last_error
    last_error = error
    output = Kp * error + Ki * integral + Kd * derivative
    return output

print("Initializing... Waiting 5 seconds")
time.sleep(5)

print("Flying upward")
for i in range(10):
    pitch = mpu.get_accel_data()['y']  # should be right
    adjust = pid(pitch)
    throttle = max(min(50 + adjust, 100), 0)
    set_throttle(throttle)
    print("Battery:", read_battery_voltage(), "Pitch:", pitch, "Throttle:", throttle)
    time.sleep(0.1)

print("Flying downward")
for i in range(10):
    set_throttle(20)  # Reduce power to descend
    print("Battery:", read_battery_voltage())
    time.sleep(0.1)

print("Landing")
set_throttle(0)
