#this file contin classs use to draw buttons lists and shpaes on the screen


from tft import *

# button is a class that handel all the on screen afects of a button
class button:
    

    def __init__(self, x, y, size, name, bg_color, fg_color, select_color, is_active):
        self.x = x
        self.y = y
        self.size = size
        self.name = name
        self.bg_color = bg_color
        self.color = fg_color
        self.select = select_color
        self.is_active = is_active
        self.is_select = False
        self.is_mark = False
    
    def selectButton(self,tft, select = False, mark = False):

        if(self.is_active == True):
                
            y = int(self.y + (self.size - 10)/2)
            x = int(self.x + self.size *0.2)
            color =  WHITE
            out_line = RED

            if(select == False):
               color = self.color
            else:
               color = self.select
            
            tft.fill_round_rect(x=self.x,y=self.y,w= self.size,h= self.size,r=5,color = color)
            if(mark == True):
                out_line = self.color
            else:
                out_line = self.bg_color
            tft.draw_round_rect(x=self.x -2,y=self.y -2 ,w= self.size + 4,h= self.size + 2,r=5,color = out_line)
            tft.text_bgcolor = color
            tft.text_fgcolor = self.bg_color
            tft.text_size = 1
            tft.print_xy(x, y, self.name)
            self.is_select = select
        else:
            print ("button is not active")
 
# button_Array is a class that handel all the on screen afects of an array of buttons
class button_Array:
    
    
    def __init__(self, x, y, row, size, offset, name_list, bg_color, fg_color, sel_color):
        self.x = x
        self.y = y
        self.name_list = name_list
        self.bg_color = bg_color
        self.color = fg_color
        self.select = sel_color
        self.num_buttons = len(self.name_list)
        self.button_list = []
        self.row = row
        b_count = 0
        self.y_offset = 0
        while(b_count < self.num_buttons):
            for i in range(row):
                ne = ""
                if(isinstance(name_list[b_count], str)):
                    ne = name_list[b_count]
                else:
                    ne = str(name_list[b_count])
                self.button_list.append(button(x=x+i*(size+offset) , y=y+self.y_offset*(size+offset) , size=size, name=ne, bg_color= self.bg_color, fg_color= self.color, select_color= sel_color, is_active= True))
                b_count += 1
                if(b_count >= self.num_buttons):
                    break
            self.y_offset += 1
        

    def select_button(self, r, c, tft, select = False, mark = False):
        
        r = min(self.row         -1, max(0, r))
        c = min(self.y_offset    -1, max(0, c))
        s = min(self.num_buttons -1, r + c*self.row)
        
        self.button_list[s].selectButton(tft, select, mark)
        return s

# circle_Array is a class that handel drawing circles array on the screen 
class circle_Array:
    
    
    def __init__(self, x, y, size, offset, Color_list, outline_color=WHITE):
        self.x = x
        self.y = y
        self.Ol_color = outline_color
        self.color_list = Color_list
        self.size = size
        self.offset = offset


    def display(self,tft):
        for i in range(len(self.color_list)):
            
            tft.fill_circle(x0=self.x + i*(self.size + self.offset), y0=self.y, r=self.size, color=self.color_list[i])
            tft.draw_circle(x0=self.x + i*(self.size + self.offset), y0=self.y, r=self.size+2, color=self.Ol_color)


# list class handel the drawing of a tuple to the screen
class list:
    
    def __init__(self,x , y, row, col, Tsize):
        self.x = x
        self.y = y
        self.row = row
        self.col = col
        self.Tsize = Tsize
        self.width = [0 for i in range(row)]
        self.list = [["" for i in range(row)] for i in range(col)]

    def add_row(self, data =None):
        self.row += 1
        self.width.append(0)
        for col in self.list:
            if(data != None):
                col.append(data)
            else:
                col.append("")
    
    def add_col(self, data):
        self.col += 1
        ln = 0
        if(len(data) > self.row):
            ln = self.row
        else:
            ln = len(data)
        self.list.append(["" for i in range(self.row)])

        for r in range(ln):
            self.list[self.col -1][r] = data[r]
    
    def display(self,tft, bevels =0):
        space = 11 * (self.Tsize +bevels)
        txtof = 2 *self.Tsize
        for r in range(self.row):
            cur = 0
            for c in range(self.col):
                m = ''
                if(type(self.list[c][r]) == int):
                    m = str(self.list[c][r])
                else:
                    m = self.list[c][r]
                cur = max(len(m) ,cur)
            self.width[r] = cur * 6 *self.Tsize + txtof +1 # convert character count to pixel count
        
        tft.text_bgcolor = BLACK
        tft.text_fgcolor = WHITE
        tft.text_size = self.Tsize
        
        
        for c in range(self.col):
            offset = 0
            for r in range(self.row):
                m = ''
                if(type(self.list[c][r]) == int):
                    m = str(self.list[c][r])
                else:
                    m = self.list[c][r]
                tft.draw_rect(self.x + offset, self.y + c * space, self.width[r], space, WHITE)
                tft.print_xy(txtof+ self.x + offset, txtof+(bevels * 4)+self.y + c * space, m)
                offset += self.width[r]
                
                
# this is an exeple code use to easly emplement the following class to the OS code 
'''
from tft import *
from Ps2_Interface import*
from machine import SPI, Pin


hspi = SPI(1 ,baudrate=1000000, polarity=1, phase=1, bits=8, firstbit=SPI.LSB ,sck=Pin(14) ,mosi=Pin(13), miso=Pin(12))
ps2 = Ps2_Interface(hspi, cs=Pin(27,Pin.OUT), ready=Pin(25,Pin.OUT))
tft = SeeSysTFT()
tft.begin()
ps2.init()

tft.fill_screen(BLACK)

cl = circle_Array(20,20, 15, 20,[GREEN, RED, YELLOW, SKYBLUE])

cl.display(tft)


lst = list(0, 0, 2, 1, 2)
lst.add_row()
lst.add_col([444,"Ass","Tits"])
lst.add_col(["Babe","Ass","Tits"])
lst.add_col(["Babe","Ass","Tits"])
lst. display(tft,1)


m_row = 4
#arr = button_Array(17 , 100, m_row, 40, 15, ["test","test2","test3","test4","test5","test6","test7","test8","test","test2","test3","test4","test5","test6","test7"],BLACK, WHITE, RED)
arr = button_Array(17 , 100, m_row, 40, 15, range(4),BLACK, WHITE, RED)
for i in arr.button_list:
    i.selectButton(tft)

row = 0
col = 0
sel = m_row -1 - ((m_row -1) + (arr.y_offset -1)*m_row - (arr.num_buttons -1))
  
while(1):
    ps2.Pull()
    ps2.read_button_state()
    
    
    
    if(ps2.read_button_release(LEFT) == True):
        arr.select_button( row, col, tft, False, False)
        row -= 1
        arr.select_button( row, col, tft, False, True)

    if(ps2.read_button_release(RIGHT) == True):
        arr.select_button( row, col, tft, False, False)
        row += 1
        arr.select_button( row, col, tft, False, True)

    if(ps2.read_button_release(UP) == True):
        arr.select_button( row, col, tft, False, False)
        col -= 1
        arr.select_button( row, col, tft, False, True)

    if(ps2.read_button_release(DOWN) == True):
        arr.select_button( row, col, tft, False, False)
        col += 1
        arr.select_button( row, col, tft, False, True)
    
    if(ps2.read_button_Press(X) == True):
        arr.select_button( row, col, tft, True, True)

    if(ps2.read_button_release(X) == True):
        arr.select_button( row, col, tft, False, True)

    #row = min(arr.row        - 1, max(0, row))
    col = min(arr. y_offset  - 1, max(0, col))

            
    if(arr.num_buttons -1 < row + col*m_row):
        row = sel

'''





        
