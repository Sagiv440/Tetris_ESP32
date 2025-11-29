from micropython import const
from machine import ADC, Pin
from time import sleep_ms
from logo import *
from tft import *
import random

adc = ADC(Pin(33))
random.seed(adc.read())

tft = SeeSysTFT()

tft.begin()
tft.rotation = 1

tft.fill_screen(BLACK)

while True:
    x = random.randint(0, tft.width - IMG_WIDTH)
    y = random.randint(0, tft.height - IMG_HEIGHT)
   
    tft.draw_bitmap(x, y, img, IMG_WIDTH, IMG_HEIGHT)
    
    sleep_ms(200)