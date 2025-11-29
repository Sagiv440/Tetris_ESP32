from utime import sleep_ms, sleep_us
from spi_driver import SPIDriver
from micropython import const
import glcdfont
import ustruct
import math

BLACK       = const(0x0000) # (  0,   0,   0) 
NAVY        = const(0x000F) # (  0,   0, 128) 
DARKGREEN   = const(0x03E0) # (  0, 128,   0) 
DARKCYAN    = const(0x03EF) # (  0, 128, 128) 
MAROON      = const(0x7800) # (128,   0,   0) 
PURPLE      = const(0x780F) # (128,   0, 128) 
OLIVE       = const(0x7BE0) # (128, 128,   0) 
LIGHTGREY   = const(0xD69A) # (211, 211, 211) 
DARKGREY    = const(0x7BEF) # (128, 128, 128) 
BLUE        = const(0x001F) # (  0,   0, 255) 
GREEN       = const(0x07E0) # (  0, 255,   0) 
CYAN        = const(0x07FF) # (  0, 255, 255) 
RED         = const(0xF800) # (255,   0,   0) 
MAGENTA     = const(0xF81F) # (255,   0, 255) 
YELLOW      = const(0xFFE0) # (255, 255,   0) 
WHITE       = const(0xFFFF) # (255, 255, 255) 
ORANGE      = const(0xFDA0) # (255, 180,   0) 
GREENYELLOW = const(0xB7E0) # (180, 255,   0) 
PINK        = const(0xFE19) # (255, 192, 203) 
BROWN       = const(0x9A60) # (150,  75,   0) 
GOLD        = const(0xFEA0) # (255, 215,   0) 
SILVER      = const(0xC618) # (192, 192, 192) 
SKYBLUE     = const(0x867D) # (135, 206, 235) 
VIOLET      = const(0x915C) # (180,  46, 226) 

def color565(r, g, b):
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3

class SeeSysTFT(object):
    # ili9341 initialization commands
    _SWRST    = const(0x01)
    _SLPOUT   = const(0x11)
    _GAMMASET = const(0x26)
    _3GMFUNCD = const(0xf2)
    _DISPON   = const(0x29)
    _PIXFMT   = const(0x3A)
    _FRMCTR1  = const(0xB1)
    _DFUNCTR  = const(0xB6)
    _PWCTR1   = const(0xC0)
    _PWCTR2   = const(0xC1)
    _VMCTR1   = const(0xC5)
    _VMCTR2   = const(0xC7)
    _GMCTRP1  = const(0xE0)
    _GMCTRN1  = const(0xE1)
    
    # ili9341 rotation commands
    _MADCTL  = const(0x36)
    _MAD_MY  = const(0x80)
    _MAD_MX  = const(0x40)
    _MAD_MV  = const(0x20)
    _MAD_BGR = const(0x08)
    
    # ili9341 gfx commands
    _CASET = const(0x2A)
    _PASET = const(0x2B)
    _RAMWR = const(0x2C)
    
    # xpt2046 commands
    _GETX  = const(0xD0)
    _GETY  = const(0x90)
    _GETZ1 = const(0xB0)
    _GETZ2 = const(0xC0)
    
    # tft specific constants
    _HEIGHT = const(320)
    _WIDTH  = const(240)
    
    def __init__(self):
        # Initialize the spi driver
        self._spi_driver      = SPIDriver()
        self._ili9341_begin   = self._spi_driver.ili9341_begin
        self._ili9341_end     = self._spi_driver.ili9341_end
        self._xpt2046_begin   = self._spi_driver.xpt2046_begin
        self._xpt2046_end     = self._spi_driver.xpt2046_end
        self._write_command   = self._spi_driver.write_command
        self._write_data      = self._spi_driver.write_data
        self._write_read_data = self._spi_driver.write_read_data
        
        # Set display parameters
        self._rotation = 0
        self._height   = _HEIGHT
        self._width    = _WIDTH
        
        # Set gfx parameters
        self._addr_row = 0xFFFF
        self._addr_col = 0xFFFF
        
        # Set calibration parameters
        self._calibration = [
        #   [ x0,   x1,  y0,   y1]
            [220, 3660, 220, 3460], # rotation = 0
            [220, 3460, 220, 3660], # rotation = 1
            [220, 3660, 380, 3480], # rotation = 2
            [380, 3480, 220, 3660]  # rotation = 3
        ]
        
        # Set default calibration (rotation = 0)
        self._cal_x0 = self._calibration[self._rotation][0]
        self._cal_x1 = self._calibration[self._rotation][1]
        self._cal_y0 = self._calibration[self._rotation][2]
        self._cal_y1 = self._calibration[self._rotation][3]
        
        # Set touch parameters 
        self._touch_x = 0
        self._touch_y = 0
        
        # Set text parameters
        self._font         = glcdfont
        self._text_fgcolor = BLACK
        self._text_bgcolor = WHITE
        self._text_size    = 1
        self._text_x       = 0
        self._text_y       = 0
        
#================================================PUBLIC API================================================
# The PUBLIC API is for the end user of the library.
  
    #================================================SIMPLE ILI9341================================================
    
    @property
    def rotation(self):
        return self._rotation
        
    @rotation.setter
    def rotation(self, rotation):        
        self._ili9341_begin()
        
        self._write_command(_MADCTL)
        rotation %= 4
               
        if rotation == 0:
            data = ustruct.pack("B", _MAD_MX | _MAD_BGR)
            self._height = _HEIGHT
            self._width  = _WIDTH
        elif rotation == 1:
            data = ustruct.pack("B", _MAD_MV | _MAD_BGR)
            self._height = _WIDTH
            self._width  = _HEIGHT     
        elif rotation == 2:
            data = ustruct.pack("B", _MAD_MY | _MAD_BGR)
            self._height = _HEIGHT
            self._width  = _WIDTH    
        elif rotation == 3:
            data = ustruct.pack("B", _MAD_MX | _MAD_MY | _MAD_MV | _MAD_BGR)
            self._height = _WIDTH
            self._width  = _HEIGHT    
            
        self._write_data(data)
        
        sleep_us(10)
        
        self._ili9341_end()
        
        self._rotation = rotation
        self._update_calibration()
        self._addr_row = 0xFFFF
        self._addr_col = 0xFFFF
        
    def is_valid_xy(self, x, y):
        if (x < 0) or (y < 0) or (x >= self._width) or (y >= self._height):
            return False
        else:
            return True
    
    def begin(self):
        self._ili9341_begin()
        
        self._write_command(_SWRST) 
        sleep_ms(150)                 
        
        self._write_command(0xef)
        self._write_data(b'\x03\x80\x02')
        self._write_command(0xcf)
        self._write_data(b'\x00\xc1\x30')
        self._write_command(0xed)
        self._write_data(b'\x64\x03\x12\x81')
        self._write_command(0xe8)
        self._write_data(b'\x85\x00\x78')
        self._write_command(0xcb)
        self._write_data(b'\x39\x2c\x00\x34\x02')
        self._write_command(0xf7)
        self._write_data(b'\x20')
        self._write_command(0xea)
        self._write_data(b'\x00\x00')
        
        self._write_command(_PWCTR1)          
        self._write_data(b'\x23')
        self._write_command(_PWCTR2)          
        self._write_data(b'\x10')
        self._write_command(_VMCTR1)      
        self._write_data(b'\x3e\x28')
        self._write_command(_VMCTR2)          
        self._write_data(b'\x86')
        self._write_command(_MADCTL)          
        self._write_data(b'\x48')
        self._write_command(_PIXFMT)          
        self._write_data(b'\x55')
        self._write_command(_FRMCTR1)     
        self._write_data(b'\x00\x13')
        self._write_command(_DFUNCTR) 
        self._write_data(b'\x08\x82\x27')
        self._write_command(_3GMFUNCD)        
        self._write_data(b'\x00')
        self._write_command(_GAMMASET)        
        self._write_data(b'\x01')
        self._write_command(_GMCTRP1)                                  
        self._write_data(b'\x0f\x31\x2b\x0c\x0e\x08\x4e\xf1\x37\x07\x10\x03\x0e\x09\x00')
        self._write_command(_GMCTRN1)                  
        self._write_data(b'\x00\x0e\x14\x03\x11\x07\x31\xc1\x48\x08\x0f\x0c\x31\x36\x0f')

        self._write_command(_SLPOUT) 
        
        sleep_ms(120)
         
        self._write_command(_DISPON) 
         
        self._ili9341_end()
    
    @property
    def height(self):
        return self._height
    
    @property
    def width(self):
        return self._width
    
    #================================================SIMPLE XPT2046================================================
    
    def is_touched(self, threshold = 350):
        valid = 0
        buf = []
        self._xpt2046_begin()
        for sample in range(5):
            if self._valid_touch(threshold):
                self._correct_rotation()
                buf.append([self._touch_x, self._touch_y])
                valid += 1
        self._xpt2046_end()
        if valid > 0:
            self._touch_x = sum([c[0] for c in buf]) // len(buf)
            self._touch_y = sum([c[1] for c in buf]) // len(buf)
            self._normalize()
            return True
        else:
            return False
    
    @property
    def calibration(self):
        return self._calibration
    
    @calibration.setter
    def calibration(self, calibration):
        if len(calibration) is not 4:
            return
        
        for rotation in range(4):
            if len(calibration[rotation]) is not 4:
                return
            for index in range(4):
                if not isinstance(calibration[rotation][index], int):
                    return
                
        self._calibration = calibration
        self._update_calibration()
    
    @property
    def touch_x(self):
        return self._touch_x
    
    @property
    def touch_y(self):
        return self._touch_y
    
    #================================================BITMAP================================================
    
    def draw_bitmap(self, x, y, img, w, h):
        self._ili9341_begin()
        
        self._set_window(x, y, x + w - 1, y + h - 1)
        self._write_data(img)
        
        self._ili9341_end()
        
    #================================================SIMPLE TEXT================================================
    
    def print_xy(self, x, y, text):
        if self.is_valid_xy(x, y):
            self._text_x = x
            self._text_y = y
            self.print(text)
    
    def print_args(self, *args):
        for arg in args:
            self.print(str(arg))
    
    def print(self, text):
        scale   = self._text_size
        fgcolor = ustruct.pack(">H", self._text_fgcolor) * scale 
        bgcolor = ustruct.pack(">H", self._text_bgcolor) * scale
        char_h  = self._font.HEIGHT * scale
        char_w  = self._font.WIDTH  * scale
        x       = self._text_x
        y       = self._text_y
        
        self._ili9341_begin()
        
        lines     = text.split('\n')
        last_line = len(lines) - 1
        for index, line in enumerate(lines):
            line_w = x + len(line) * char_w
            if(line_w > self._width):
                discard = (self._width - line_w) // char_w 
                line = line[:discard]
            for char in line:
                pixels = self._glyph_pixels(char, char_h, char_w, scale, fgcolor, bgcolor)
                self._set_window(x, y, x + char_w - 1, y + char_h - 1)
                self._write_data(pixels)
                x += char_w
            if len(lines) > 1 and index != last_line:
                next_line_pos = char_h + 1
                if(y + next_line_pos + char_h <= self._height):
                    y += next_line_pos
                else:
                    return
                x = 0
        self._text_x = x
        self._text_y = y
            
        self._ili9341_end()
    
    @property
    def text_fgcolor(self):
        return self._text_fgcolor
    
    @text_fgcolor.setter
    def text_fgcolor(self, fgcolor):
        self._text_fgcolor = fgcolor
    
    @property
    def text_bgcolor(self):
        return self._text_bgcolor
    
    @text_bgcolor.setter
    def text_bgcolor(self, bgcolor):
        self._text_bgcolor = bgcolor
   
    @property
    def text_size(self):
        return self._text_size
   
    @text_size.setter
    def text_size(self, size):
        if size > 5:
            size = 5
        elif size < 1:
            size = 1
        self._text_size = size
    
    @property
    def text_x(self):
        return self._text_x
    
    @text_x.setter
    def text_x(self, x):
        if (x >= 0) and (x < self._width):
            self._text_x = x
    
    @property
    def text_y(self):
        return self._text_y
    
    @text_y.setter
    def text_y(self, y):
        if (y >= 0) and (y < self._height):
            self._text_y = y
            
    #================================================SIMPLE GFX================================================
       
    def draw_round_rect(self, x, y, w, h, r, color):
        self._ili9341_begin()
        
        self._push_hline(x + r  , y    , w - r - r, color)     
        self._push_hline(x + r  , y + h - 1, w - r - r, color) 
        self._push_vline(x    , y + r  , h - r - r, color)     
        self._push_vline(x + w - 1, y + r  , h - r - r, color) 
        
        self._push_draw_corner(x + r    , y + r    , r, 1, color)
        self._push_draw_corner(x + w - r - 1, y + r    , r, 2, color)
        self._push_draw_corner(x + w - r - 1, y + h - r - 1, r, 4, color)
        self._push_draw_corner(x + r    , y + h - r - 1, r, 8, color)
        
        self._ili9341_end()
    
    def draw_circle(self, x0, y0, r, color):
        x  = 0
        dx = 1
        dy = r + r
        p  = -(r >> 1)    
        
        self._ili9341_begin()
        
        self._push_pixel(x0 + r, y0, color)
        self._push_pixel(x0 - r, y0, color)
        self._push_pixel(x0, y0 - r, color)
        self._push_pixel(x0, y0 + r, color)
        
        while x < r:
            if p >= 0:
                dy -= 2
                p  -= dy
                r  -= 1
            
            dx += 2
            p  += dx
            x  += 1
            
            self._push_pixel(x0 + x, y0 + r, color)
            self._push_pixel(x0 - x, y0 + r, color)
            self._push_pixel(x0 - x, y0 - r, color)
            self._push_pixel(x0 + x, y0 - r, color)

            self._push_pixel(x0 + r, y0 + x, color)
            self._push_pixel(x0 - r, y0 + x, color)
            self._push_pixel(x0 - r, y0 - x, color)
            self._push_pixel(x0 + r, y0 - x, color)
        
        self._ili9341_end()

    def draw_triangle(self, x0, y0, x1, y1, x2, y2, color):
        self._ili9341_begin()
        
        self._push_line(x0, y0, x1, y1, color)
        self._push_line(x1, y1, x2, y2, color)
        self._push_line(x2, y2, x0, y0, color)
        
        self._ili9341_end()

    def draw_rect(self, x, y, w, h, color):
        self._ili9341_begin()
        
        self._push_hline(x, y, w, color)             
        self._push_hline(x, y + h - 1, w, color)     
        self._push_vline(x, y+1, h-2, color)         
        self._push_vline(x + w - 1, y+1, h-2, color) 
        
        self._ili9341_end()
    
    def draw_angled_line(self, x0, y0, r, angle, color):
        x = x0 + r * math.cos(angle * math.pi / 180)
        y = y0 + r * math.sin(angle * math.pi / 180)
        x1 = round(x)
        y1 = round(y)
        self.draw_line(x0, y0, x1, y1, color)
    
    def draw_line(self, x0, y0, x1, y1, color):
        self._ili9341_begin()
        
        self._push_line(x0, y0, x1, y1, color)
                
        self._ili9341_end()
        
    def draw_pixel(self, x, y, color):
        self._ili9341_begin()
        
        self._push_pixel(x, y, color)
        
        self._ili9341_end()
    
    def fill_round_rect(self, x, y, w, h, r, color):
        self._ili9341_begin() 
        
        self._push_rect(x, y + r, w, h - r - r, color)
        
        self._push_fill_corner(x + r, y + h - r - 1, r, 1, w - r - r - 1, color)
        self._push_fill_corner(x + r    , y + r, r, 2, w - r - r - 1, color)
        
        self._ili9341_end()
    
    def fill_circle(self, x0, y0, r, color):
        x  = 0
        dx = 1
        dy = r + r
        p  = -(r >> 1)
        
        self._ili9341_begin()
        
        self._push_hline(x0 - r, y0, dy+1, color)
        
        while x < r:
            if p >= 0:
                dy -= 2
                p  -= dy
                r  -= 1
                
            dx += 2
            p  += dx
            x  += 1
            
            self._push_hline(x0 - r, y0 + x, 2 * r+1, color)
            self._push_hline(x0 - r, y0 - x, 2 * r+1, color)
            self._push_hline(x0 - x, y0 + r, 2 * x+1, color)
            self._push_hline(x0 - x, y0 - r, 2 * x+1, color)
        
        self._ili9341_end()
        
    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0
        if y1 > y2:
            y2, y1 = y1, y2
            x2, x1 = x1, x2
        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0
        
        self._ili9341_begin()
        
        if y0 == y2:
            a = x0
            b = x0
            if x1 < a:
                a = x1
            elif x1 > b:
                b = x1
            if x2 < a:
                a = x2
            elif x2 > b:
                b = x2
            self._push_hline(a, y0, b - a + 1, color)
            return
        
        dx01 = x1 - x0
        dy01 = y1 - y0
        dx02 = x2 - x0
        dy02 = y2 - y0
        dx12 = x2 - x1
        dy12 = y2 - y1
        sa   = 0
        sb   = 0
        
        if y1 == y2:
            last = y1
        else:
            last = y1 - 1
        
        y = y0
        while y <= last:
            a   = x0 + sa // dy01
            b   = x0 + sb // dy02
            sa += dx01
            sb += dx02
            
            if a > b:
                a, b = b, a
            
            self._push_hline(a, y, b - a + 1, color)
            
            y += 1
            
        sa = dx12 * (y - y1)
        sb = dx02 * (y - y0)
        while y <= y2:
            a   = x1 + sa // dy12
            b   = x0 + sb // dy02
            sa += dx12
            sb += dx02
            
            if a > b:
               a, b = b, a
               
            self._push_hline(a, y, b - a + 1, color)
            
            y += 1
            
        self._ili9341_end()
        
    def fill_rect(self, x, y, w, h, color):
        self._ili9341_begin()

        self._push_rect(x, y, w, h, color)

        self._ili9341_end()
        
    def fill_screen(self, color):
        self.fill_rect(0, 0, self._width, self._height, color)
        
#================================================PRIVATE API================================================
# The PRIVATE API is for the developer only! DO NOT USE these functions if you
# are not sure what you are doing!
    
    #================================================XPT2046 CORE================================================
    
    _RAWERR = const(20)
    
    @micropython.native
    def _valid_touch(self, threshold):
        z1 = 1
        z2 = 0
        while z1 > z2:
            z2 = z1
            z1 = self._get_raw_z()
            sleep_ms(1)
            
        if z1 <= threshold:
            return False

        x1, y1 = self._get_raw_xy()
    
        sleep_ms(1)
        
        if self._get_raw_z() <= threshold:
            return False
        
        sleep_ms(2)
        
        x2, y2 = self._get_raw_xy()
        
        if abs(x1 - x2) > _RAWERR:
            return False
        if abs(y1 - y2) > _RAWERR:
            return False
        
        self._touch_x = x1
        self._touch_y = y1
        
        return True
    
    @micropython.native
    def _update_calibration(self):
        self._cal_x0 = self._calibration[self._rotation][0]
        self._cal_x1 = self._calibration[self._rotation][1]
        self._cal_y0 = self._calibration[self._rotation][2]
        self._cal_y1 = self._calibration[self._rotation][3]
    
    @micropython.native
    def _correct_rotation(self):
        x = self._touch_x
        y = self._touch_y
            
        if self._rotation == 0: 
            y = 4095 - y
        elif self._rotation == 1:
            x = 4095 - self._touch_y
            y = 4095 - self._touch_x
        elif self._rotation == 2:
            x = 4095 - x
        elif self._rotation == 3:
            x = self._touch_y
            y = self._touch_x
            
        self._touch_x = x
        self._touch_y = y
   
    @micropython.native
    def _normalize(self):
        x = self._touch_x
        y = self._touch_y
    
        x = (x - self._cal_x0) * self._width / self._cal_x1;
        y = (y - self._cal_y0) * self._height / self._cal_y1;
    
        self._touch_x = int(x)
        self._touch_y = int(y)
    
    @micropython.native
    def _get_raw_xy(self):
        x = self._write_read_data(_GETX, 12)
        y = self._write_read_data(_GETY, 12)
        return x, y
    
    @micropython.native
    def _get_raw_z(self):
        z  = 0xFFF
        z += self._write_read_data(_GETZ1, 12)
        z -= self._write_read_data(_GETZ2, 12)
        return z
    
    #================================================TEXT CORE================================================
    
    _PIXEL_SIZE = const(2)
    
    @micropython.native
    def _glyph_pixels(self, char, height, width, scale, fgcolor, bgcolor):
        pixels = bytearray((width * _PIXEL_SIZE) * height)
        mvpixels = memoryview(pixels)
        glyph   = self._font.get_ch(char)
        pixel_w = _PIXEL_SIZE * scale
        for row in range(0, width, scale):
            line = glyph[row // scale]
            for col in range(0, height, scale):
                if line & 0x1:
                    color = fgcolor
                else:
                    color = bgcolor
                for offset in range(scale):
                    index = (row * _PIXEL_SIZE) + ((col + offset) * _PIXEL_SIZE) * width
                    mvpixels[index:index+pixel_w] = color
                line >>= 1
        return mvpixels
    
    #================================================GFX CORE================================================
        
    @micropython.native
    def _push_draw_corner(self, x0, y0, r, cornername, color):
        f     = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x     = 0
        
        while(x < r):
            if f >= 0:
                r     -= 1
                ddF_y += 2
                f     += ddF_y
                
            x     += 1
            ddF_x += 2
            f     += ddF_x
             
            if cornername & 0x1:
                self._push_pixel(x0 - r, y0 - x, color)
                self._push_pixel(x0 - x, y0 - r, color)
            if cornername & 0x2: 
                self._push_pixel(x0 + x, y0 - r, color)
                self._push_pixel(x0 + r, y0 - x, color)
            if cornername & 0x4:
                self._push_pixel(x0 + x, y0 + r, color)
                self._push_pixel(x0 + r, y0 + x, color)
            if cornername & 0x8: 
                self._push_pixel(x0 - r, y0 + x, color)
                self._push_pixel(x0 - x, y0 + r, color)
                
    @micropython.native
    def _push_fill_corner(self, x0, y0, r, cornername, delta, color):
        f     = 1 - r
        ddF_x = 1
        ddF_y = -r - r
        y     = 0
        
        delta += 1
        
        while y < r:
            if f >= 0:
                ddF_y += 2
                f     += ddF_y
                r     -= 1
            
            ddF_x += 2
            f     += ddF_x
            y     += 1
            
            if cornername & 0x1:
                self._push_hline(x0 - r, y0 + y, r + r + delta, color)
                self._push_hline(x0 - y, y0 + r, y + y + delta, color)
            if cornername & 0x2:
                self._push_hline(x0 - r, y0 - y, r + r + delta, color)
                self._push_hline(x0 - y, y0 - r, y + y + delta, color)      
                
    @micropython.native
    def _push_line(self, x0, y0, x1, y1, color):
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        
        dx = x1 - x0
        dy = abs(y1 - y0)

        err   = dx >> 1
        ystep = -1
        xs    = x0
        dlen  = 0

        if y0 < y1:
            ystep = 1
        
        if steep:
            while x0 <= x1:
                dlen += 1
                err  -= dy
                if err < 0:
                    err += dx
                    if dlen == 1:
                        self._push_pixel(y0, xs, color)
                    else:
                        self._push_vline(y0, xs, dlen, color)
                    dlen = 0
                    y0  += ystep
                    xs   = x0 + 1
                x0 += 1
            if dlen:
                self._push_vline(y0, xs, dlen, color)
        else:
            while x0 <= x1:
                dlen += 1
                err  -= dy
                if err < 0:
                    err += dx
                    if dlen == 1:
                        self._push_pixel(xs, y0, color)
                    else:
                        self._push_hline(xs, y0, dlen, color)
                    dlen = 0
                    y0  += ystep
                    xs   = x0 + 1
                x0 += 1
            if dlen:
                self._push_hline(xs, y0, dlen, color)
                
    @micropython.native
    def _push_hline(self, x, y, w, color):
        if (y < 0) or (x >= self._width) or (y >= self._height):
            return
    
        if x < 0:
            w += x
            x = 0 
        
        if (x + w) > self._width:
            w = self._width  - x
        
        if w < 1:
            return
        
        self._set_window(x, y, x + w - 1, y)
        self._push_color(color, w)
        
    @micropython.native
    def _push_vline(self, x, y, h, color):
        if (x < 0) or (x >= self._width) or (y >= self._height):
            return

        if y < 0:
            h += y
            y = 0

        if (y + h) > self._height:
            h = self._height - y

        if h < 1:
            return
        
        self._set_window(x, y, x, y + h - 1)
        self._push_color(color, h)
            
    @micropython.native
    def _push_rect(self, x, y, w, h, color):
        if (x >= self._width) or (y >= self._height):
            return

        if x < 0:
            w += x
            x = 0 
        if y < 0:
            h += y
            y = 0

        if (x + w) > self._width:
            w = self._width  - x
        if (y + h) > self._height:
            h = self._height - y

        if (w < 1) or (h < 1):
            return
        
        self._set_window(x, y, x + w - 1, y + h - 1)
        self._push_color(color, w * h)
    
    @micropython.native
    def _set_window(self, x0, y0, x1, y1):
        self._write_command(_CASET) 
        self._write_data(ustruct.pack(">HH", x0, x1))
        self._write_command(_PASET) 
        self._write_data(ustruct.pack(">HH", y0, y1))
        self._write_command(_RAMWR)
        self._addr_col = 0xFFFF
        self._addr_row = 0xFFFF
    
    @micropython.native
    def _push_color(self, color, length):
       chunks, rest = divmod(length, 512)
       if chunks:
           data = ustruct.pack(">H", color) * 512
           for count in range(chunks):
               self._write_data(data)
       if rest:
           data = ustruct.pack(">H", color) * rest
           self._write_data(data)
    
    @micropython.native
    def _push_pixel(self, x, y, color):
        if self.is_valid_xy(x, y):
            if self._addr_col != x:
                self._write_command(_CASET)
                self._write_data(ustruct.pack(">HH", x, x))
                self._addr_col = x
            if self._addr_row != y:
                self._write_command(_PASET)
                self._write_data(ustruct.pack(">HH", y, y))
                self._addr_row = y
            self._write_command(_RAMWR)
            self._write_data(ustruct.pack(">H", color))