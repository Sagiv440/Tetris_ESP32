import machine, time
import ustruct
from micropython import const
from machine import Pin


START   = const(3)
SELECT  = const(0) 
UP      = const(4)
DOWN    = const(6)
LEFT    = const(7)
RIGHT   = const(5)
L1      = const(10)
L2      = const(8)
L3      = const(1)
R1      = const(11)
R2      = const(9)
R3      = const(2)
X       = const(14)
SQU     = const(15)
TRI     = const(12)
O       = const(13)

class Ps2_Interface:


    def __init__(self, spi, cs, ready):
        self.spi = spi
        self.cs = cs
        self.ready = ready

        self.command = ['\0' for i in range(9)]
        #self.rest = ['\0' for i in range(12)]

        self.command[0] = chr(1)

        self.PS2data = ['\0' for i in range(21)] #hold the data of both the digital and anlog inpout of the current state
        self.last_state= [False for i in range(16)] #hold the last state of all the buttons on the controller
        self.button_state= [False for i in range(16)] #hold the current state of all the buttons on the controller

    
    def init (self):                        #function to initialized the controller
        self.Pull()   
        self.ConfigMode(1)
        self.AnalogMode()
        self.ConfigMode(0)

#function for reading a byte to the controller by writing on the clk rising edge and reading on the clk falling edge

    def readWritePS2(self,cmd): # the main interface function for comunicate with the controller
        last_read = 0
        self.cs.value(0)
        self.ready.value(1)
        time.sleep_us(60)    # delay time for the controller to syncronise

        for i in range(len(cmd)): # transmiting the command byte one by one and updating the data registers (PS2data)
            #print("for value {} packte is".format(ord(cmd[i])))
            #print(ustruct.pack('b',ord(cmd[i])))
            

            x = self.spi.read(1,ord(cmd[i])) #function for reading a byte to the controller by writing on the clk rising edge and reading on the clk falling edge
            self.PS2data[i] = x
            #print(x)

        self.cs.value(1) # deselect the controller  
        self.ready.value(0)
        
    def read_button_state(self): # update the digital stats of the controller buttons in to boolean list (button_state)
        chack = 1
        for i in range(8):
            self.last_state[i] = self.button_state[i]
            if(ord(self.PS2data[3]) & (chack << i) != 0):
                self.button_state[i] = False
            else:
                self.button_state[i] = True

        for i in range(8):
            self.last_state[i+8] = self.button_state[i+8]
            if (ord(self.PS2data[4]) & (chack << i) != 0):
                self.button_state[i+8] = False
            else:
                self.button_state[i+8] = True

    def read_button_release(self, button): # return true if the selected button was release
        state = False
        if(self.button_state[button] == False and self.last_state[button] == True):
            state = True
        return state
    
    def read_button_Press(self, button): # return true if the selected button was pressd
        state = False
        if(self.button_state[button] == True and self.last_state[button] == False):
            state = True
        return state
    
    def read_button_Held(self, button): # return true if the selected button was held
        self.last_state[button] = self.button_state[button]
        return self.button_state[button]
    
    def Pull(self):
        self.command[1] = chr(0x42)
        self.readWritePS2(self.command)
    
    def ConfigMode(self, enter = 0):
        self.command[1] = chr(0x43)
        self.command[3] = chr(enter)
        self.readWritePS2(self.command)
        self.command[3] = chr(0)
    

    def AnalogMode(self):
        self.command[1] = chr(0x44)
        self.command[3] = chr(1)
        self.command[4] = chr(3)
        self.readWritePS2(self.command)
        self.command[3] = chr(0)
        self.command[3] = chr(0)


'''
hspi = SPI(1 ,baudrate=1000000, polarity=1, phase=1, bits=8, firstbit=SPI.LSB ,sck=Pin(14) ,mosi=Pin(13), miso=Pin(12))
ps2 = Ps2_Interface(hspi, cs=Pin(27,Pin.OUT), ready=Pin(25,Pin.OUT))



ps2.init()


while(1):
    ps2.Pull()
    ps2.read_button_state()

    if(ps2.read_button_release(SELECT) == True):
        print(" Select button was pressd")
    if(ps2.read_button_release(L3) == True):
        print(" L3 button was pressd")
    if(ps2.read_button_release(2) == True):
        print(" R3 button was pressd")
    if(ps2.read_button_release(3) == True):
        print(" Start button was pressd")
    if(ps2.read_button_release(4) == True):
        print(" Up button was pressd")
    if(ps2.read_button_release(5) == True):
        print(" Right button was pressd")
    if(ps2.read_button_release(6) == True):
        print(" Down button was pressd")
    if(ps2.read_button_release(7) == True):
        print(" Left button was pressd")
    if(ps2.read_button_release(8) == True):
        print(" L2 button was pressd")
    if(ps2.read_button_release(9) == True):
        print(" R2 button was pressd")
    if(ps2.read_button_release(10) == True):
        print(" L1 button was pressd")
    if(ps2.read_button_release(11) == True):
        print(" R1 button was pressd")
    if(ps2.read_button_release(12) == True):
        print(" Triangle button was pressd")
    if(ps2.read_button_release(13) == True):
        print(" O button was pressd")
    if(ps2.read_button_release(X) == True):
        print(" X button was Release")
    if(ps2.read_button_Press(X) == True):
        print(" X button was pressd")
    if(ps2.read_button_release(15) == True):
        print(" Square button was pressd")
        
    #print ("the X and Y analog value of the joysicks")
    #----------------------------------------------------------------------
    #print(" RS_X {} RS_Y {}".format(ord(ps2.PS2data[5]),ord(ps2.PS2data[6])))
    #print(" LS_X {} LS_Y {}".format(ord(ps2.PS2data[7]),ord(ps2.PS2data[8])))

    #time.sleep_ms(500)
'''
 


