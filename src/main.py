from tft import *
from Ps2_Interface import *
from button_menu import *
from machine import Pin, SPI
from keyboard import ps2_keyboard
import network 



def main(tft, ps2):

    tft.fill_screen(BLACK)
    tft.text_bgcolor = BLACK
    tft.text_fgcolor = WHITE
    tft.text_size = 5
    tft.print_xy(24,3,"Tetris")
    tft.text_size = 1
    tft.print_xy(1,310,"By Sharon and Sagiv")

    arr = button_Array(15 , 150, 3, 60, 15, ["Option","Play","Network"], BLACK, WHITE, RED)

    for i in arr.button_list:
        i.selectButton(tft)

    row = 0
    col = 0
    value = 0
  
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

        if(ps2.read_button_release(X) == True):
            arr.select_button( row, col, tft, True, True)
            value = row
            break

        row = min(arr.row        - 1, max(0, row))
        col = min(arr. y_offset  - 1, max(0, col))
    if(value == 0):
        return 5 # Net_connect
    elif(value == 1):
        return 3 # Titris
    elif(value == 2):
        return 4 # Network
    return 3



def Option(tft, ps2, Network, Keyboard):
    x = 20
    y = 30
    tft.fill_screen(BLACK)
    tft.text_bgcolor = BLACK
    tft.text_fgcolor = WHITE
    tft.text_size = 5
    tft.print_xy(16,5,"Options")
    tft.text_size = 1
    tft.print_xy(1,310,"By Sharon and Sagiv")
    tft.print_xy(0,60," Set the Network and games settings.")
    tft.print_xy(0,240," Use the Arrow keys to move.\n 'x' => Select \n 'O' => Back to main menu\n 'Start' => Confirm")

    m_row = 2
    arr = button_Array(52 , 150, m_row, 60, 15, ["Network","Game"], BLACK, WHITE, RED)

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
        
        if(ps2.read_button_Press(X) == True):
            arr.select_button( row, col, tft, True, True)

        if(ps2.read_button_release(X) == True):
            arr.select_button( row, col, tft, False, True)
            return Option_Switch(row + col*m_row ,tft, ps2, Network, Keyboard)

        if(ps2.read_button_release(O) == True):
            return [2,-1,-1]

        row = min(arr.row        - 1, max(0, row))
        col = min(arr. y_offset  - 1, max(0, col))

                
        #if(arr.num_buttons -1 < row + col*m_row):
            #row = sel


def Option_Switch(argument, tft, ps2, station, Keyboard):
    switcher = {
        0: Net_connect,
        1: Game,

    }
    # Get the function from switcher dictionary
    func = switcher.get(argument, lambda: "Invalid month")
    # Execute the function
    return func(tft, ps2, station, Keyboard)


def Net_connect(tft, ps2, station, keyboard):
    
    import wifi_boot as wifi
    tft.fill_screen(BLACK)
    tft.text_bgcolor = BLACK
    tft.text_fgcolor = WHITE
    tft.text_size = 1
    tft.print_xy(1,310,"By Sharon and Sagiv")
    
    if(station.isconnected() == False):
        #user = keybord.write_string("Enter The Network name","Network :")
        user = Net_Scan(tft, ps2, station)
        if(type(user) == int):
            return  [5,-1,-1] # Options 

        password = keyboard.write_string("Enter The Network password","Password :")
        
        try:
            s.bind(('', 80))
            s.listen(5)
        except:
            print("connect")

        tft.fill_screen(BLACK)
        tft.text_size = 1
        tft.print_xy(0,160,"  Connecting to {}".format(user))
        
        wifi.connect(user, password, station)

        tft.fill_screen(BLACK)
        if(station.isconnected()):
            tft.print_xy(0,150,"user is connected to {}".format(user))
            print("user is connected to {}".format(user))
        else:
            
            tft.print_xy(0,150," Error:\n\n Connection unsuccessful")
            print(" Error:\n\n Connection unsuccessful")
    else:
        
        tft.print_xy(0,150,"  user is alrady connected \n  to the internet")
        print('  user is alrady connected \n  to the internet')
        tft.print_xy(0,185,"    Press '[]' to Disconnect")

    tft.print_xy(0,200,"    Press 'O' to Return")

    while(1):
        ps2.Pull()
        ps2.read_button_state()
        if(station.isconnected() and ps2.read_button_release(SQU)):
            station.disconnect()
            
            break
        if(ps2.read_button_release(O) == True):
            break
    return  [5,-1,-1] # Options
    
def Net_Scan(tft, ps2, Network):
    x = 20
    y = 80
    tft.fill_screen(BLACK)
    tft.text_bgcolor = BLACK
    tft.text_fgcolor = WHITE
    tft.text_size = 5
    tft.print_xy(16,5,"Network")
    tft.text_size = 1
    tft.print_xy(1,310,"By Sharon and Sagiv")
    tft.print_xy(30,100,"Scanning...")
    keybord = ps2_keyboard(tft,ps2)
    Network.active(True)  
    wifi = Network.scan()
    tft.print_xy(30,100,"           ")
    m_row = 1
    lst = list(x=x + 25 , y=y, row=1, col=0, Tsize=1)
    for i in wifi:
        lst.add_col([i[0].decode()])

    arr = button_Array( x=x , y=y+1, row=m_row, size=20, offset=2, name_list= range(1,len(wifi)+1), bg_color=BLACK, fg_color=WHITE, sel_color=RED)
    lst.display(tft,1)

    for i in arr.button_list:
        i.selectButton(tft)

    row = 0
    col = 0
    sel = m_row -1 - ((m_row -1) + (arr.y_offset -1)*m_row - (arr.num_buttons -1))
      
    while(1):
        ps2.Pull()
        ps2.read_button_state()
        

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
            return wifi[col][0].decode()

        if(ps2.read_button_release(O) == True):
            return -1

        #row = min(arr.row        - 1, max(0, row))
        col = min(arr. y_offset  - 1, max(0, col))

                
        if(arr.num_buttons -1 < row + col*m_row):
            row = sel
   
def Game(tft, ps2, station, Keyboard):
    print("test_1")
    tft.fill_screen(BLACK)
    tft.text_bgcolor = BLACK
    tft.text_fgcolor = WHITE
    tft.text_size = 3
    tft.print_xy(12,5,"Game Settings")
    tft.text_size = 1
    tft.print_xy(1,310,"By Sharon and Sagiv")
    
    
    
    m_row = 3
    arr = button_Array(45 , 100, m_row, 40, 15, ["Easy","Mid","Hard"],BLACK, WHITE, RED)

    m_col = 1 
    col_y = 170 # hold the y value of the color select menu
    col_x = 29
    arr2 = button_Array(col_x , col_y, m_col, 30, 10, range(3),BLACK, WHITE, RED) 

    color1 = circle_Array(x=col_x + 51, y=col_y + 15, size=15, offset=25, Color_list=[GREEN, RED, YELLOW, SKYBLUE], outline_color=WHITE)
    color2 = circle_Array(x=col_x + 51, y=col_y + 55, size=15, offset=25, Color_list=[ORANGE, RED, PINK, MAGENTA], outline_color=WHITE)
    color3 = circle_Array(x=col_x + 51, y=col_y + 95, size=15, offset=25, Color_list=[CYAN, VIOLET, GREEN, SKYBLUE], outline_color=WHITE)
    
    tft.print_xy(45,85,"Set the difficalty")
    tft.print_xy(col_x,156,"Set the Color palette")
    for i in arr.button_list + arr2.button_list:
        i.selectButton(tft)

    
    color1.display(tft)
    color2.display(tft)
    color3.display(tft)
    
    row = 0
    col = 0
    cl = 0
    lv = 0
    select = False  
    while(1):
        ps2.Pull()
        ps2.read_button_state()
        
        
        
        if(ps2.read_button_release(LEFT) == True):
            arr.select_button( row, 0, tft, False, False)
            row -= 1
            select = True
            arr.select_button( row, 0, tft, False, True)

        if(ps2.read_button_release(RIGHT) == True):
            arr.select_button( row, 0, tft, False, False)
            row += 1
            select = True
            arr.select_button( row, 0, tft, False, True)

        if(ps2.read_button_release(UP) == True):
            arr2.select_button( 0, col, tft, False, False)
            col -= 1
            select = False
            arr2.select_button( 0, col, tft, False, True)

        if(ps2.read_button_release(DOWN) == True):
            arr2.select_button( 0, col, tft, False, False)
            col += 1
            select = False
            arr2.select_button( 0, col, tft, False, True)

        if(ps2.read_button_Press(X) == True):
            if(select):
                arr.select_button( row, 0, tft, True, True)
                lv = row
            else:
                arr2.select_button( 0, col, tft, True, True)
                cl = col

        if(ps2.read_button_release(X) == True):
            if(select):
                arr.select_button( row, 0, tft, True, True)
            else:
                arr2.select_button( 0, col, tft, True, True)

        if(ps2.read_button_release(O) == True):
            return [5,-1,-1] 
        
        if(ps2.read_button_release(START) == True):
           
            return [5,cl,lv] 

        row = min(arr.row        - 1, max(0, row))
        col = min(arr2. y_offset  - 1, max(0, col))
        
                

       
'''
hspi = SPI(1 ,baudrate=1000000, polarity=1, phase=1, bits=8, firstbit=SPI.LSB ,sck=Pin(14) ,mosi=Pin(13), miso=Pin(12))
ps2 = Ps2_Interface(hspi, cs=Pin(27,Pin.OUT), ready=Pin(25,Pin.OUT))
tft = SeeSysTFT()
keybord = ps2_keyboard(tft,ps2)
station = network.WLAN(network.STA_IF)
station.active(True)
tft.begin()

Option(tft, ps2, station, keybord)
'''
