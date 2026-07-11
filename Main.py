from machine import Pin, ADC, PWM
import time

potentiometer = ADC(Pin(34))
potentiometer.atten(ADC.ATTN_11DB)
potentiometer.width(ADC.WIDTH_12BIT)

servo = PWM(Pin(27))
servo.freq(50)

while True:
    pot_value = potentiometer.read()
    angle = int(pot_value / 4095 * 180)
    duty = int(40 + (angle / 180) * 80)
    servo.duty(duty)
    time.sleep(0.1)
