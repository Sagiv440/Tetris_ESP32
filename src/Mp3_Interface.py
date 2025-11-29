from machine import UART
import time
import utime
import ustruct as struct

class mp3_Interface:
    def __init__(self, uart):
        self.uart = uart
        self.uart.init(9600, bits=8, parity=None, stop=1)
        self.command = [0x7e, 0xff, 0x06, 0x00, 0x00, 0x00, 0x00, 0xef]


    def regWrite(self, com, feedBack, data): #the only data that we have to change for other command
        self.command[3] = com
        self.command[4] = feedBack
        self.command[5], self.command[6] =  divmod(data, 256)

        for i in range (8):

            dt = struct.pack("B",self.command[i]) #command for encode the value to unsigned char 
            #print("data {} decoded {}".format(self.command[i],dt))
            self.uart.write(dt)


    def NextSong(self):
        self.regWrite(0x01, 0x00, 0x00)

    def PrevSong(self):
        self.regWrite(0x02, 0x00, 0x00)

    def SelectSong(self, NumSong=0):
        self.regWrite(0x03, 0x00, NumSong)
    
    def SelectSong(self, NumSong=0, time = 0):
        if(time <= 0):
            self.regWrite(0x03, 0x00, NumSong)
    
    def VolUp(self):
        self.regWrite(0x04, 0x00, 0x00)

    def VolDown(self):
        self.regWrite(0x05, 0x00, 0x00)

    def SetVol(self,NumVol):
        if (NumVol > 30):
           NumVol = 30
        self.regWrite(0x06, 0x00, NumVol)

    def ResetSong(self):
        self.regWrite(0x0c, 0x00, 0x00)

    def PlaySong(self):
        self.regWrite(0x0d, 0x00, 0x00)

    def PauseSong(self):
        self.regWrite(0x0e, 0x00, 0x00)

    def CycleSongInFolder(self, folder = 1):
        data = folder << 8 | 2
        self.regWrite(0x17, 0x00, data)


#play song number 6, wait 10 sec, go to next song , wait 10 sec, change to volume, wait 10 sec and the volume to the max  
'''
uart = UART(2, 9600)
print(uart)
mp3 = mp3_Interface(uart)
for i in range(7):
    print("test song number {}".format(i))
    mp3.SelectSong(i)
    time.sleep(1)

for i in range(1,4):
    print("test song number {}".format(i))
    mp3.CycleSongInFolder(i)
    time.sleep(2)
'''