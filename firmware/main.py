from machine import Pin, PWM, I2C, ADC
import time
from MPU6050 import MPU6050
import bmp180

# motor
motor_pins = [18, 17, 3, 4]  # [FL, FR, BL, BR]
motors = [PWM(Pin(p), freq=20000, duty_u16=0) for p in motor_pins]

# batt
adc_battery = ADC(Pin(15))
adc_battery.atten(ADC.ATTN_11DB)

i2c = I2C(0, scl=Pin(8), sda=Pin(7))
time.sleep(1)
mpu = MPU6050(i2c)
bmp = bmp180.BMP085(i2c)

# pid
class PID:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.last_error = 0
        self.integral = 0

    def compute(self, target, current):
        error = target - current
        self.integral += error
        derivative = error - self.last_error
        self.last_error = error
        return self.Kp * error + self.Ki * self.integral + self.Kd * derivative

def mix_motors(throttle, pitch_corr, roll_corr, yaw_corr):
    motor_values = [0, 0, 0, 0]  # FL, FR, BL, BR
    motor_values[0] = throttle + pitch_corr + roll_corr - yaw_corr
    motor_values[1] = throttle + pitch_corr - roll_corr + yaw_corr
    motor_values[2] = throttle - pitch_corr + roll_corr + yaw_corr
    motor_values[3] = throttle - pitch_corr - roll_corr - yaw_corr

    for i in range(4):
        duty = int(max(min(motor_values[i], 100), 0) / 100 * 65535)
        motors[i].duty_u16(duty)

def read_battery_voltage():
    raw = adc_battery.read()
    voltage = (raw / 4095) * 3.3 * 2
    return voltage

pid_pitch = PID(1.2, 0.0, 0.3)
pid_roll = PID(1.2, 0.0, 0.3)
pid_yaw = PID(0.8, 0.0, 0.2)
pid_x = PID(0.6, 0.01, 0.2)
pid_y = PID(0.6, 0.01, 0.2)
pid_z = PID(1.0, 0.02, 0.3)

waypoints = [
    (0, 0, 1.0),
    (1, 0, 1.0),
    (1, 1, 1.2),
    (0, 1, 1.0),
    (0, 0, 0.5)
]

position = [0.0, 0.0, 0.0]
velocity = [0.0, 0.0, 0.0]
last_time = time.ticks_ms()

baseline_altitude = bmp.read_altitude()

def update_position(accel):
    global last_time, velocity, position
    now = time.ticks_ms()
    dt = time.ticks_diff(now, last_time) / 1000.0
    last_time = now

    for i, axis in enumerate(['x', 'y']):
        a = accel[axis]
        velocity[i] += a * dt
        position[i] += velocity[i] * dt

    position[2] = bmp.read_altitude() - baseline_altitude

print("init... waiting 5 seconds")
time.sleep(5)

for wp in waypoints:
    print("moving to:", wp)
    reached = False
    timeout = time.ticks_ms() + 10000

    while not reached and time.ticks_ms() < timeout:
        accel = mpu.get_accel_data()
        gyro = mpu.get_gyro_data()

        update_position(accel)

        x_corr = pid_x.compute(wp[0], position[0])
        y_corr = pid_y.compute(wp[1], position[1])
        z_corr = pid_z.compute(wp[2], position[2])

        pitch_corr = pid_pitch.compute(x_corr, accel['y'])
        roll_corr = pid_roll.compute(y_corr, accel['x'])
        yaw_corr = pid_yaw.compute(0, gyro['z'])

        base_throttle = 50 + z_corr
        mix_motors(base_throttle, pitch_corr, roll_corr, yaw_corr)

        print(f"pos: {position}, alt: {bmp.read_altitude():.2f}m, batt: {read_battery_voltage():.2f}V")
        time.sleep(0.1)

        if all(abs(position[i] - wp[i]) < 0.2 for i in range(3)):
            reached = True

print("landing")
for i in range(20):
    mix_motors(20 - i, 0, 0, 0)
    time.sleep(0.1)
mix_motors(0, 0, 0, 0)
