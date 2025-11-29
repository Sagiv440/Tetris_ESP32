# This file is executed on every boot (including wake-boot from deepsleep)
import network  
import ubinascii as ub

try:
  import usocket as socket
except:
  import socket

from Ps2_Interface import Ps2_Interface
from Tetris import Tetris as ts

from machine import Pin, SPI, UART
from  Mp3_Interface import mp3_Interface
import main as mn
import wifi_boot as wifi
import high_score as Page
from tft import *
from keyboard import ps2_keyboard

hspi = SPI(1 ,baudrate=1000000, polarity=1, phase=1, bits=8, firstbit=SPI.LSB ,sck=Pin(14) ,mosi=Pin(13), miso=Pin(12))  # reprisent the Hardware SPI controller no the ESP
vspi = SPI(2 , 80000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18) ,mosi=Pin(23), miso=Pin(19)) # reprisent the  Vetrual SPI controller no the ESP
uart = UART(2, 9600) # reprisent the UART controller no the ESP
mp3 = mp3_Interface(uart) # reprisent the mp3 player
tft = SeeSysTFT()  # reprisent the tft display 

station = network.WLAN(network.STA_IF) # reprisent the wifi network controller on the ESP

ps2 = Ps2_Interface(hspi, cs=Pin(27,Pin.OUT), ready=Pin(25,Pin.OUT)) # reprisent the Playstatin2 controller 
keybord = ps2_keyboard(tft,ps2) # reprisent a softwere implemnted keyboard


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # reprisent the network protokols use to transmint to the internet( Networking = IPv4, Transport = TCP)
score_table = [[1, "Sagiv",600],[2, "Sharon", 300],[3, "Sharon", 0],[4, "Sharon", 0],[5, "Sharon", 0]] # holds the High score table
 
settings = [0,0] # hold the game settings
Color_palat = [[BLACK, GREEN, RED, YELLOW, SKYBLUE], #hold the color palette used to color the game shapes
                [BLACK, ORANGE, RED, PINK, MAGENTA],
                [BLACK, CYAN, VIOLET, GREEN, SKYBLUE]]

sysmode = 0 # hold the current mode the OS is on
thismod = sysmode #hold the last mode the OS was on

#------------------------------------------------------------------------------------------------------------------------
# update_high_score: takes an integer "score" and a name "text" 
# and updates the score_table reletive to the new "score"
#----------------------------------------------------------------------------------------------------------------------
def update_high_score(score, text):
    for T in range(len(score_table)):
        if(score_table[T][2] < score):
            i = len(score_table)-1
            for j in range(len(score_table)-1-T):
                score_table[i][2] =  score_table[i - 1][2]
                score_table[i][1] =  score_table[i - 1][1]
                score_table[i][0] =  i+1
                i -= 1

            score_table[T][2] =  score
            score_table[T][1] =  text
            score_table[T][0] =  T+1
            break

#------------------------------------------------------------------------------------------------------------------------
# Boot is cold ones on reseting and is incharg of initiating
# all the extern IO (Playstatin2 controller , tft display)
#----------------------------------------------------------------------------------------------------------------------
def Boot():
    global sysmode
    global thismod
    tft.begin() # initiating the tft display
    ps2.init() # initiating the Playstatin2 controller
    tft.fill_screen(BLACK) 
    sysmode = 1  #Boot

    return "Boot"

#------------------------------------------------------------------------------------------------------------------------
# main cols the main function  that is incharge of handling the main menu of the OS
#----------------------------------------------------------------------------------------------------------------------
def Main():
    global sysmode
    global thismod
    thismod = sysmode
    #mp3.CycleSongInFolder(1) # play main scren backgraund music

    sysmode = mn.main(tft,ps2) # colls the main scren function
  
  
def Reset_Screen():
    global sysmode
    global thismod
    thismod = sysmode
    mp3.CycleSongInFolder(1) # play main scren backgraund music
    sysmode = 2  #Boot

#------------------------------------------------------------------------------------------------------------------------
# Tetris function creats a new tetris game and coll it's playGame function 
# after that the function updates the score_table
#----------------------------------------------------------------------------------------------------------------------
def Tetris():
    global sysmode
    global thismod
    thismod = sysmode
    
    tetris = ts( tft, 16, ps2, mp3, settings[1], Color_palat[settings[0]]) # creats a new Tetris game
    tetris.playGame() #start the game
    tft.fill_screen(BLACK) # chage OS to clear screen mode 
    text = keybord.write_string("Enter your name","name :") # colls the keyboard to return a name that was enterd by the user

    update_high_score(tetris.scorre,text) # update the score table with the last score from the game
    sysmode = 1 #Main

#------------------------------------------------------------------------------------------------------------------------
# Network tern on the High_score website (the ESP need to be connected to a network)
#----------------------------------------------------------------------------------------------------------------------    
def Network():
    global sysmode
    global thismod
    thismod = sysmode
    tft.text_bgcolor = BLACK
    tft.text_fgcolor = WHITE
    tft.text_size = 1
    tft.fill_screen(BLACK) # clear screen

    try: # in case of en error dering the configrations
        s.bind(('', 80)) # config the network portocol to send the data thrue port 80
        s.listen(5) # config the network portocol to recived data thrue port 5
    except:
        print("connect")
    if(station.isconnected()): # chack if the ESP is connectd to a netwrok
       
        
        ip = station.ifconfig() # Get the IP of the ESP given from the router
        print(ip[0]) 
        tft.print_xy(0,310," "+ip[0]) #Print the ESP IP on the screen
        exit = False  
        
        while(exit == False): # wait until the user close the webpage
            exit = Page.Page_refresh(s, score_table) # Send the HTML code to the network

        print('exit page')

        sysmode = 2 # Main
    else:
        tft.print_xy(0,210,"  deivce is offline\n\n Pleas connect to a Network\n\n   Press X to exit")
        print("  deivce is offline\n\n Pleas connect to a Network\n\n   Press X to exit")
    while(sysmode == thismod):
        
        ps2.Pull()
        ps2.read_button_state()
        if(ps2.read_button_release(14) == True):
            sysmode = 2 # Main
    return "Network"
    
#------------------------------------------------------------------------------------------------------------------------
# Options handle all the setting of Network and the tetris game
#----------------------------------------------------------------------------------------------------------------------
def Options():
    global sysmode
    global thismod
    thismod = sysmode
    #mp3.CycleSongInFolder(3) #play backgraund music
    tft.fill_screen(BLACK)
    
    data = mn.Option(tft = tft, ps2 = ps2, Network = station, Keyboard = keybord) # cols the Options main menu and return a list to update the game setting if thay have bin updated
    print(data)
    print(settings)
    sysmode = data[0] # haenged the mode of the OS 
    if(data[1] > -1): # chack if the data returnd from the Option menu is relevent and updates the game settings veribles 
        settings[1] = data[2] # holds the difficlty settings verible
        settings[0] = data[1] # holds the color settings verible
    
    print("Color setting: {}, Level settings: {}".format(settings[0], settings[1]))
    return "Options screen"

#------------------------------------------------------------------------------------------------------------------------
# Net_test used to test the network abilitis of the ESP (not used in the main OS)
#----------------------------------------------------------------------------------------------------------------------
def Net_test():
    global sysmode
    global thismod
    thismod = sysmode
    
    tft.fill_screen(BLACK)
    if(station.isconnected() == False):
        user = 'LGD855'
        password = 'm8234760'
        try:
            s.bind(('', 80))
            s.listen(5)
        except:
            print("connect")

        tft.fill_screen(BLACK)
        tft.print_xy(0,160,"  Connecting to {}".format(user))

        wifi.connect(user, password)

        tft.fill_screen(BLACK)
        tft.print_xy(0,150,"user is connected to {}".format(user))
    else:
        tft.print_xy(0,150,'  user is alrady connected \n  to the internet')
        print('  user is alrady connected \n  to the internet')
        
    sysmode = 2 # Main
    return "Net_test"

#------------------------------------------------------------------------------------------------------------------------
# Main_Switch used to Switch between the different modes and of the OS 
#----------------------------------------------------------------------------------------------------------------------
def Main_Switch(argument):
    switcher = {
        0: Boot,
        1: Reset_Screen,
        2: Main,
        3: Tetris,
        4: Network,
        5: Options,
        6: Net_test,
    }
    # Get the function from switcher dictionary
    func = switcher.get(argument, lambda: "Invalid month")
    # Execute the function
    return func()

while(1): #Main Loop of the OS
    Main_Switch(sysmode)


        
