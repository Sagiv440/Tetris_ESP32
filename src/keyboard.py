from Ps2_Interface import *
from machine import Pin, SPI, UART
from button_menu import *
from tft import *


class ps2_keyboard:
    def __init__(self, tft, ps2):
        self.display = tft
        self.ps2 = ps2
        self.key_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'
                         ,'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'
                         ,'0','1','2','3','4','5','6','7','8','9']
                            
        

    def select_leter(self, row, index):
        
        return self.key_list[index]

    def write_string(self, title, context):
        lst = []
        index = 0
        enter = False
        print(self.key_list)
        self.display.fill_screen(BLACK)
        self.display.text_bgcolor = BLACK
        self.display.text_fgcolor = WHITE
        self.display.text_size = 2
        self.display.print_xy(24,0,"String Keyboard")
        self.display.text_size = 1
        self.display.print_xy(8,130,title)
        self.display.print_xy(0,310,"By: Sharon and Sagiv")
        m_row = 13
        
        arr = button_Array(8 , 160, m_row, 15, 2, self.key_list, BLACK, WHITE, RED)

        for i in arr.button_list:
            i.selectButton(self.display)
        
        self.ps2.init()
        row = 0
        col = 0
        sel = m_row -1 - ((m_row -1) + (arr.y_offset -1)*m_row - (arr.num_buttons -1))
            
        while(1):
            self.ps2.Pull()
            self.ps2.read_button_state()
            
            
            
            if(self.ps2.read_button_release(LEFT) == True or ord(self.ps2.PS2data[7]) < 40 ):
                arr.select_button( row, col, self.display, False, False)
                row -= 1
                arr.select_button( row, col, self.display, False, True)

            if(self.ps2.read_button_release(RIGHT) == True or ord(self.ps2.PS2data[7]) > 200 ):
                arr.select_button( row, col, self.display, False, False)
                row += 1
                arr.select_button( row, col, self.display, False, True)

            if(self.ps2.read_button_release(UP) == True or ord(self.ps2.PS2data[8]) < 40 ):
                arr.select_button( row, col, self.display, False, False)
                col -= 1
                arr.select_button( row, col, self.display, False, True)

            if(self.ps2.read_button_release(DOWN) == True or ord(self.ps2.PS2data[8]) > 200 ):
                arr.select_button( row, col, self.display, False, False)
                col += 1
                arr.select_button( row, col, self.display, False, True)

            if(self.ps2.read_button_Press(X) == True):
                arr.select_button( row, col, self.display, True, True)
                lst.append(self.key_list[row + col*m_row])

            if(self.ps2.read_button_release(X) == True):
                arr.select_button( row, col, self.display, False, True)

            if(self.ps2.read_button_release(SQU) == True):
                arr.select_button( row, col, self.display, True, True)
                lst.append(' ')
            
            if(self.ps2.read_button_release(O) == True):
                if(len(lst) != 0):
                    lst.pop(len(lst)-1)
            
            if (self.ps2.read_button_release(START) == True):
                enter = True
                return "".join(lst)

            col = min(arr. y_offset  - 1, max(0, col))
            
            if(arr.num_buttons -1 < row + col*m_row):
                row = sel
            
            self.display.text_bgcolor = BLACK
            self.display.text_fgcolor = WHITE
            self.display.print_xy(8,140,context +"".join(lst)+"  ")


'''
hspi = SPI(1 ,baudrate=1000000, polarity=1, phase=1, bits=8, firstbit=SPI.LSB ,sck=Pin(14) ,mosi=Pin(13), miso=Pin(12))
tft = SeeSysTFT()
tft.begin()
ps2.init()
ps2 = Ps2_Interface(hspi, cs=Pin(27,Pin.OUT), ready=Pin(25,Pin.OUT))
keybord = ps2_keyboard(tft,ps2)
keybord.write_string("Enter your name","name :")
'''

