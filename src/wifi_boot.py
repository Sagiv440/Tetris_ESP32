import utime

def connect(user, password, station):

    import esp
    esp.osdebug(None)

    import gc
    gc.collect()

    station.active(True)
    station.connect(user, password)
    
    print("connecting to : {}".format(user))

    time = 0.0
    while station.isconnected() == False:
        tm = utime.ticks_us()
        time += (utime.ticks_us() - tm)/1000000
        if(station.isconnected() == True):
            print('Connection successful')
            print(station.ifconfig())
            break
        if(time >= 2.0 ):
            station.disconnect()
            print('Error Connection unsuccessful')
            break
    print('user is alrady connected to the Network')
'''
try:
  import usocket as socket
except:
  import socket

from machine import Pin
import network  
station = network.WLAN(network.STA_IF)
connect('LGD855','m8234760', station)
'''