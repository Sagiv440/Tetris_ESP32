import random as rd
import machine ,utime
import ustruct
from machine import Pin, SPI, UART
from Ps2_Interface import *
from  Mp3_Interface import mp3_Interface
from tft import *

class Tetris:
    
    
    class Vector2(object):
        def __init__(self, X, Y):
            self.x = X
            self.y = Y

    pass

    class shape:
        def __init__(self):
            self.id = 1
            self.x = 5
            self.y = 2
            self.vector = []

        def rotateLeft(self):
            for i in self.vector:
                x_0 = i.x
                y_0 = i.y
                i.x = y_0
                i.y = -x_0

        def rotateRight(self):
            for i in self.vector:
                x_0 = i.x
                y_0 = i.y
                i.x = -y_0
                i.y = x_0

        def detectCollidoin(self, world, width, height):
            for i in self.vector:
                if (self.x + i.x < 0 or self.x + i.x >= width):
                    print("the X axis is out of border {}".format(self.x + i.x ))
                    return True

                if (self.y + i.y < 0 or self.y + i.y >= height):
                    print("the Y axis is out of border {}".format(self.y + i.y))
                    return True

                if (world[self.x + i.x + (self.y + i.y) * width] != 0):
                    print("the the space is ocupide ,space value {}, X pos {}, Y pos {}".format(world[self.x + i.x + (self.y + i.y) * width], self.x + i.x, self.y + i.y))
                    return True
            return False


    def __init__(self, display, block_size, ps2, mp3, difficalty = 0, colorP = [BLACK, GREEN, RED, YELLOW, SKYBLUE]):
        self.display = display
        self.ps2 = ps2
        self.mp3 = mp3
        self.scorre = 0
        self.scoreLevel = 0
        self.GameOver = False
        self.block_S = block_size
        self.index = 2
        self.inColor = 0
        self.screenx = 240
        self.screeny = 320
        self.nWorldWidth = 12
        self.nWorldHeight = 18
        self.curShape = []
        self.world = [0 for i in range(12 * 18)]
        self.old_world = [0 for i in range(12 * 18)]
        self.colorP = colorP
        self.init_Shapes()
        self.tm = 0 
        self.Dtime = 0.0 # hold the framesTime
        self.Gtime = 0.0 # hold the time sycle of every move 
        self.time = 0.0 
        self.difficalty = 2.5
        if(difficalty > 2):
            self.Point_exe = 2
        elif(difficalty < 0):
            self.Point_exe = 0
        else:
            self.Point_exe = difficalty

    def init_Shapes(self): #Create all the shapes of the game
        for i in range(7):
            self.curShape.append(self.shape()) # Create the shape objects
        
        # Create the vectors for the shape 0
        self.curShape[0].vector.append(self.Vector2(-1, 0))
        self.curShape[0].vector.append(self.Vector2(0, 0))
        self.curShape[0].vector.append(self.Vector2(1, 0))
        self.curShape[0].vector.append(self.Vector2(0, 1))
        
        # Create the vectors for the shape 1
        self.curShape[1].vector.append(self.Vector2(-1, 0))
        self.curShape[1].vector.append(self.Vector2(0, 0))
        self.curShape[1].vector.append(self.Vector2(1, 0))
        self.curShape[1].vector.append(self.Vector2(1, 1))
        
        # Create the vectors for the shape 2
        self.curShape[2].vector.append(self.Vector2(-1, 0))
        self.curShape[2].vector.append(self.Vector2(0, 0))
        self.curShape[2].vector.append(self.Vector2(1, 0))
        self.curShape[2].vector.append(self.Vector2(-1, 1))
        
        # Create the vectors for the shape 3
        self.curShape[3].vector.append(self.Vector2(-1, 0))
        self.curShape[3].vector.append(self.Vector2(0, 0))
        self.curShape[3].vector.append(self.Vector2(0, 1))
        self.curShape[3].vector.append(self.Vector2(1, 1))
        
        # Create the vectors for the shape 4
        self.curShape[4].vector.append(self.Vector2(-1, 1))
        self.curShape[4].vector.append(self.Vector2(0, 1))
        self.curShape[4].vector.append(self.Vector2(0, 0))
        self.curShape[4].vector.append(self.Vector2(1, 0))
        
        # Create the vectors for the shape 5
        self.curShape[5].vector.append(self.Vector2(0, 0))
        self.curShape[5].vector.append(self.Vector2(0, 1))
        self.curShape[5].vector.append(self.Vector2(1, 1))
        self.curShape[5].vector.append(self.Vector2(1, 0))

        # Create the vectors for the shape 6
        self.curShape[6].vector.append(self.Vector2(0, -1))
        self.curShape[6].vector.append(self.Vector2(0, 0))
        self.curShape[6].vector.append(self.Vector2(0, 1))
        self.curShape[6].vector.append(self.Vector2(0, 2))

    def resetShape(self):
        self.index = rd.randint(0, 6)
        self.curShape[self.index].id = rd.randint(1, 4)   
        self.curShape[self.index].x = 6
        self.curShape[self.index].y = 1

    def chackLine(self, i):
        y = i
        for x in range(self.nWorldWidth):
            if(self.world[x + y * self.nWorldWidth] == 0):
                return False
        return True

    def deletLine(self, i):
        y = i
        
        while(y > 1):
            for x in range(self.nWorldWidth):
                self.world[x + y * self.nWorldWidth] = self.world[x + (y - 1) * self.nWorldWidth]
            y -= 1

    def rotateShapeL(self): #rotate the shape to the left
        self.curShape[self.index].rotateLeft()
        if (self.curShape[self.index].detectCollidoin(self.world, self.nWorldWidth, self.nWorldHeight) == True):
            self.curShape[self.index].rotateRight()

    def rotateShapeR(self): #rotate the shape to the right
        self.curShape[self.index].rotateRight()
        if (self.curShape[self.index].detectCollidoin(self.world, self.nWorldWidth, self.nWorldHeight) == True):
            self.curShape[self.index].rotateLeft()

    def moveLR(self, i): # move the shape main index Left or Right one world position
        self.curShape[self.index].x += i
        if (self.curShape[self.index].detectCollidoin(self.world, self.nWorldWidth, self.nWorldHeight) == True):
            self.curShape[self.index].x -= i

    def moveDown(self): # move the shape main index Down one world position
        self.curShape[self.index].y += 1
        if (self.curShape[self.index].detectCollidoin(self.world, self.nWorldWidth, self.nWorldHeight) == True):
            self.curShape[self.index].y -= 1

    def removeShape(self): # remove the shape + shape vectors from the world array
        for i in self.curShape[self.index].vector:
            self.world[self.curShape[self.index].x + i.x + (self.curShape[self.index].y + i.y) * self.nWorldWidth] = 0

    def appendShape(self):  # append the shape + the shape vectors to the world array
        for i in self.curShape[self.index].vector:
            self.world[self.curShape[self.index].x + i.x + (self.curShape[self.index].y + i.y) * self.nWorldWidth] = self.curShape[self.index].id

    def onUserCreate(self):
        self.GameOver = False
        self. scorre = 0
        self.difficalty = 2.5
        self.mp3.SelectSong(11) #play music before starting the game
        utime.sleep(3.5)
        self.resetShape()
        for i in self.curShape[self.index].vector:
            self.world[(self.curShape[self.index].x + i.x) + (self.curShape[self.index].y + i.y) * self.nWorldWidth] = self.curShape[self.index].id
        self.time = 0


    def onUserUpdate(self):
        self.tm = utime.ticks_ms()
          
        if(self.GameOver == False):
            
            if(self.time > 0):
                self.time -= self.Dtime

            if(self.Gtime > 0): 
                self.Gtime -= self.Dtime
                print("frame time: {}".format(self.Dtime))
            
            if(self.scorre >= self.scoreLevel + 1500 - (500*self.Point_exe) and self.difficalty > 0):
                print("difficalty: {}".format(self.difficalty))
                self.difficalty -= 0.5 
                self.scoreLevel = self.scorre

            if(self.ps2.read_button_Held(LEFT) == True):
                self.mp3.SelectSong(12, self.time) #move the shape to the left 
                self.removeShape()
                self.moveLR(-1)
                self.appendShape()

            if (self.ps2.read_button_Held(RIGHT) == True):
                self.mp3.SelectSong(12, self.time) #move the shape to the right
                self.removeShape()
                self.moveLR(1)
                self.appendShape()

            if (self.ps2.read_button_Press(L1) == True):
                self.mp3.SelectSong(14, self.time) #rotate the shape to the left
                self.removeShape()
                self.rotateShapeL()
                self.appendShape()
            
            if (self.ps2.read_button_Press(R1) == True):
                self.mp3.SelectSong(14, self.time) #rotate the shape to the right
                self.removeShape()
                self.rotateShapeR()
                self.appendShape()
            
            if (self.ps2.read_button_Held(DOWN) == True):
                self.mp3.SelectSong(14, self.time) #move shape down
                self.Gtime = 0
            
            if(self.Gtime <= 0):
                self.Gtime = self.difficalty
                self.removeShape()
                self.curShape[self.index].y += 1
                if (self.curShape[self.index].detectCollidoin(self.world, self.nWorldWidth, self.nWorldHeight) == True):  # chack if shape has colided width othter shape
                    self.curShape[self.index].y -= 1 
                    if(self.curShape[self.index].y == 1):
                        self.GameOver = True
                        return
                    self.appendShape()  
                    self.resetShape()
                    self.scorre += 50;
                    y = self.nWorldHeight - 1
                    line_count = 0
                    while(y > 0):  # scanne every line in the world to scann for full lins 
                        if(self.chackLine(y) == True): # if a full line was found the game will be deleted and all the blocks will above it will move down one world position
                            line_count += 1
                            self.deletLine(y)

                        else:
                            y -= 1

                    if(line_count > 0): # if line were deleted
                        self.time = 15
                        self.mp3.SelectSong(13) #play song for delete line

                    if(line_count == 1):
                        self.scorre += 200

                    elif(line_count == 2 ):
                        self.scorre += 400
                        self.difficalty += 0.25

                    elif(line_count == 3 ):
                        self.scorre += 800
                        self.difficalty += 0.5

                    elif(line_count == 4):
                        self.scorre += 1000
                        self.difficalty += 1.0
                            
                else:  
                    self.appendShape()
            
    
        # Clear Screen
        for i in self.curShape[self.index].vector:
            self.world[(self.curShape[self.index].x + i.x) + (self.curShape[self.index].y + i.y) * self.nWorldWidth] = self.curShape[self.index].id  # x + y * width

        self.Dtime = (utime.ticks_ms() - self.tm)/10

    
    def printScreen(self):
        x_offset = int((self.screenx -(self.block_S* self.nWorldWidth))/2)
        y_offset = 25
        for y in range(self.nWorldHeight):
           
            for x in range(self.nWorldWidth):
                if(self.world[x + y * self.nWorldWidth] != self.old_world[x + y * self.nWorldWidth]):
                    self.display._spi_driver._block(x_offset + 1+ x *  self.block_S ,y_offset+  1+ y * self.block_S , x_offset + (x + 1) * self.block_S - 1,
                                   y_offset+ (y + 1) * self.block_S - 1, ustruct.pack(self.display._spi_driver._ENCODE_PIXEL, self.colorP[self.world[x + y * self.nWorldWidth]]) * self.block_S * self.block_S)
                    self.old_world[x + y * self.nWorldWidth] = self.world[x + y * self.nWorldWidth]

    def playGame(self):
        
        self.display.fill_screen(BLUE)
        self.display.fill_rect(24,25,192,288,BLACK)
        self.onUserCreate()
        self.display.text_x = 0
        self.display.text_y = 0
        self.display.text_bgcolor = BLUE
        self.display.text_fgcolor = WHITE
        self.display.text_size = 3
        #self.display._spi_driver.ili9341_begin()
        while(self.GameOver == False):
                    self.display._spi_driver.ili9341_begin()
                #timeing

                #input
                    self.ps2.Pull()
                    self.ps2.read_button_state()
                #logic
                    self.onUserUpdate()
                #print screen
                    self.printScreen()
                    self.display.print_xy(24,0,"score: {}".format(self.scorre))

        self.display._spi_driver.ili9341_end()




