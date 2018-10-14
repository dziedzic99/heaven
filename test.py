import arm
import busio
import board
from time import sleep
i2c = busio.I2C(board.SCL, board.SDA)
laser = arm.Laser(i2c=i2c)
while True:
    print()