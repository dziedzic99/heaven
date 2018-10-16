from PCA9685 import PCA9685
from VL53L0X import VL53L0X
from ADS1015 import ADS1015

import busio
import board

from constants import *

# ----- PHYSICAL CLASSES -----


class Encoders(ADS1015):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getangle(self, segmentnumber):
        return self.read_adc(segmentnumber)*270/1600


class Laser(VL53L0X):
    def __init__(self, **kwargs):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        super().__init__(i2c=self.i2c, **kwargs)


class Servos(PCA9685):
    def __init__(self, zeroes, **kwargs):
        super().__init__(**kwargs)
        self.zeroes = zeroes

    def move(self, segmentnumber, speed):
        pwm = round(speed + self.zeroes[segmentnumber])
        if pwm < CONST_MIN_PWM:
            pwm = CONST_MIN_PWM
        if pwm > CONST_MAX_PWM:
            pwm = CONST_MAX_PWM
        super().set_pwm(segmentnumber, 0, pwm)

    def stop(self, segmentnumber):
        self.move(segmentnumber, 0)


# ----- ABSTRACT CLASSES -----


class Claw:
    def __init__(self, portnumber, isclosed=True):
        self.portnumber = portnumber
        self.closed = isclosed

    def close(self):
        self.servos.move(self.portnumber, CONST_CLAW_CLOSED)

    def open(self):
        self.servos.move(self.portnumber, CONST_CLAW_OPEN)


class Segments:
    def __init__(self,
                 lengths,
                 min_angles, max_angles,
                 initial_angles, encoders, servos
                 ):
        self.lengths = lengths
        self.min_angles = min_angles
        self.max_angles = max_angles
        self.angles = initial_angles
        self.encoders = encoders
        self.servos = servos

    def __setanglephysical__(self, segmentnumber, new_angle):
        while abs(new_angle-self.encoders.getangle(segmentnumber))>CONST_ANGLE_ACCURACY:
            self.servos.move(segmentnumber, (new_angle-self.encoders.getangle(segmentnumber))*CONST_SPEED_FACTOR)
        self.servos.stop(segmentnumber)

    def setangle(self, segmentnumber, new_angle):
        if self.min_angles[segmentnumber] <= new_angle <= self.max_angles[segmentnumber]:
            self.angles[segmentnumber] = new_angle
            self.__setanglephysical__(segmentnumber, new_angle)
        else:
            raise ValueError('Angle out of range')

    def getangle(self, segmentnumber):
        return self.angles[segmentnumber]


# ----- AGGREGATING CLASS -----


class Arm:
    def __init__(self, numberofsegments, segmentlength, minangles, maxangles, zeroes, initialangles, baserotation=0):
        self.encoders = Encoders
        self.servos = Servos(zeroes)
        self.laser = Laser()
        self.claw = Claw(CONST_CLAW_PORT, self.servos)
        self.segments = Segments(segmentlength, minangles, maxangles, initialangles, self.encoders, self.servos)
        self.numberofsegments = numberofsegments
        self.baserotation = baserotation

    def getangle(self, segmentnumber):
        return self.segments.getangle(segmentnumber)

    def stop(self):
        for i in range(self.numberofsegments):
            self.servos.stop(i)

