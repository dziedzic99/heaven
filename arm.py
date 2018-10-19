from PCA9685 import PCA9685
from VL53L0X import VL53L0X
from ADS1015 import ADS1015

import busio
import board
import logging
from constants import *


logging.basicConfig(level=logging.WARNING)


# ----- PHYSICAL CLASSES -----


class Encoders(ADS1015):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getangle(self, segmentnumber):
        return self.read_adc(CONST_SEGMENT_ADC_PORTS[segmentnumber])*270/1600


class Laser(VL53L0X):
    def __init__(self, **kwargs):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        super().__init__(i2c=self.i2c, **kwargs)
    def range(self):
        logging.log(logging.INFO, 'Laser on')
        super().range()
        logging.log(logging.INFO, 'Laser off')


class Servos(PCA9685):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_pwm_freq(60)

    def move(self, segmentnumber, speed):
        pwm = round(speed + CONST_SEGMENT_STABLE_PWM_VALUES[segmentnumber])
        print(pwm)
        if pwm < CONST_MIN_PWM:
            pwm = CONST_MIN_PWM
        if pwm > CONST_MAX_PWM:
            pwm = CONST_MAX_PWM
        self.set_pwm(CONST_SEGMENT_MOTOR_PORTS[segmentnumber], 0, pwm)

    def moveclaw(self, state):
        if state == 0:
            self.set_pwm(CONST_CLAW_PORT, 0, CONST_CLAW_CLOSED)
        elif state == 1:
            self.set_pwm(CONST_CLAW_PORT, 0, CONST_CLAW_OPEN)
        else:
            raise ValueError('Undefined claw state requested')

    def stop(self, segmentnumber):
        self.move(segmentnumber, 0)

    def abort(self):
        super().software_reset()


# ----- GLOBAL PHYSICAL LAYER DEFINITIONS -----

encoders = Encoders()
laser = Laser()
servos = Servos()

# ----- ABSTRACT CLASSES -----


class Segments:
    def __init__(self):
        self.angles = [0 for i in range(CONST_NUMBER_OF_SEGMENTS)]

    def setanglephysical(self, segmentnumber, new_angle):
        global servos, encoders
        while abs(new_angle - encoders.getangle(segmentnumber)) > CONST_ANGLE_ACCURACY:
            servos.move(segmentnumber, (new_angle-encoders.getangle(segmentnumber))*CONST_SPEED_FACTOR)
        servos.stop(segmentnumber)

    def setangle(self, segmentnumber, new_angle):
        if CONST_MIN_ANGLES[segmentnumber] <= new_angle <= CONST_MAX_ANGLES[segmentnumber]:
            self.angles[segmentnumber] = new_angle
            self.setanglephysical(segmentnumber, new_angle)
        else:
            raise ValueError('Angle out of range')

    def getangle(self, segmentnumber):
        return self.angles[segmentnumber]


# ----- GLOBAL ABSTRACT LAYER DEFINITIONS -----

segments = Segments()

# ----- AGGREGATING CLASS -----


class Arm:
    def __init__(self, numberofsegments):
        self.numberofsegments = numberofsegments

    def getangle(self, segmentnumber):
        global segments
        return segments.getangle(segmentnumber)

    def abort(self):
        global servos
        servos.abort()


arm = Arm(3)

