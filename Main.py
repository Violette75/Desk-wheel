from machine import Pin, PWM, ADC
import time

# Config
POT_PIN = 34
TILT_PIN = 15
SERVO_PIN = 27
SERVO_MIN_DUTY = 25
SERVO_MAX_DUTY = 125
NACELLE_POSITIONS = [0, 60, 120, 180]
MODE_NORMAL = 0
MODE_CONTROLE = 1

# Initialisation
pot = ADC(Pin(POT_PIN))
pot.atten(ADC.ATTN_11DB)
pot.width(ADC.WIDTH_12BIT)
tilt = Pin(TILT_PIN, Pin.IN, Pin.PULL_UP)
servo = PWM(Pin(SERVO_PIN), freq=50)
current_mode = MODE_NORMAL
current_nacelle_index = 0
last_activity_time = time.time()
tilt_state_history = []

def set_servo_angle(angle):
    duty = int(SERVO_MIN_DUTY + (angle / 180) * (SERVO_MAX_DUTY - SERVO_MIN_DUTY))
    servo.duty(duty)

def map_pot_to_angle(pot_value):
    return int((pot_value / 4095) * 180)

def move_to_next_nacelle():
    global current_nacelle_index
    current_nacelle_index = (current_nacelle_index + 1) % len(NACELLE_POSITIONS)
    set_servo_angle(NACELLE_POSITIONS[current_nacelle_index])

def toggle_mode_controle():
    global current_mode
    if current_mode == MODE_NORMAL:
        current_mode = MODE_CONTROLE
        set_servo_angle(0)
    else:
        current_mode = MODE_NORMAL
        set_servo_angle(0)

while True:
    current_time = time.time()
    elapsed_time = current_time - last_activity_time

    tilt_state = tilt.value()
    tilt_state_history.append(tilt_state)
    if len(tilt_state_history) > 4:
        tilt_state_history.pop(0)

    if len(tilt_state_history) == 4 and tilt_state_history == [1, 0, 1, 0]:
        toggle_mode_controle()
        tilt_state_history = []
        last_activity_time = current_time

    if current_mode == MODE_NORMAL and elapsed_time >= 15 * 60 and current_nacelle_index < len(NACELLE_POSITIONS) - 1:
        move_to_next_nacelle()
        last_activity_time = current_time

    if current_mode == MODE_NORMAL and tilt.value() == 0:
        set_servo_angle(0)
        while tilt.value() == 0:
            time.sleep(0.1)
        last_activity_time = current_time

    if current_mode == MODE_CONTROLE:
        pot_value = pot.read()
        angle = map_pot_to_angle(pot_value)
        set_servo_angle(angle)
        last_activity_time = current_time
    else:
        pot_value = pot.read()
        angle = map_pot_to_angle(pot_value)
        set_servo_angle(angle)
        last_activity_time = current_time

    time.sleep(0.05)
