from micropython import const
from machine import SPI, Pin
import ustruct

class SPIDriver(object):
    # Constant spi speeds
    _ILI9341_CLOCK = const(80000000) #40mhz
    _XPT2046_CLOCK = const(2500000)  #2.5mhz
    
    # Constant spi parameters
    _MOSI       = const(23)
    _MISO       = const(19)
    _SCK        = const(18)
    _XPT2046_CS = const(5)
    _ILI9341_CS = const(15) 
    _DC         = const(4)
    _VSPI       = const(2)
    
    _COLUMN_SET = 0x2a
    _PAGE_SET = 0x2b
    _RAM_WRITE = 0x2c
    _RAM_READ = 0x2e

    _ENCODE_PIXEL = ">H"
    _ENCODE_POS = ">HH"
    _DECODE_PIXEL = ">BBB"

    
    def __init__(self):
        self._spi = SPI(_VSPI, sck=Pin(_SCK), mosi=Pin(_MOSI), miso=Pin(_MISO))
        self._spi.deinit()
        
        self._ili9341_cs = Pin(_ILI9341_CS, Pin.OUT, value=1)
        self._xpt2046_cs = Pin(_XPT2046_CS, Pin.OUT, value=1)
        self._dc         = Pin(_DC, Pin.OUT, value=1)

        self._send = bytearray(3)
        self._recv = bytearray(3)

    #================================================PUBLIC API================================================
    
    @micropython.native
    def write_read_data(self, cmd, bits):
        self._send[0] = cmd
        self._spi.write_readinto(self._send, self._recv)
        return (self._recv[1] * 256 + self._recv[2]) >> (15 - bits)

    @micropython.viper
    def write_command(self, command):
        self._dc.off()
        self._spi.write(bytearray([command]))
        self._dc.on()
    
    @micropython.viper
    def write_data(self, data):
        self._spi.write(data)
        
    @micropython.viper
    def ili9341_begin(self):
        self._spi.init(_VSPI, _ILI9341_CLOCK)
        self._ili9341_cs.off()
    
    @micropython.viper
    def ili9341_end(self):
        self._spi.deinit()
        self._ili9341_cs.on()
        
    @micropython.viper
    def xpt2046_begin(self):
        self._spi.init(_VSPI, _XPT2046_CLOCK)
        self._xpt2046_cs.off()
    
    @micropython.viper
    def xpt2046_end(self):
        self._spi.deinit()
        self._xpt2046_cs.on()


    def _block(self, x0, y0, x1, y1, data=None):
        """Read or write a block of data."""
        self._write(self._COLUMN_SET, ustruct.pack(self._ENCODE_POS, x0, x1))
        self._write(self._PAGE_SET, ustruct.pack(self._ENCODE_POS, y0, y1))
        if data is None:
            size = ustruct.calcsize(self._DECODE_PIXEL)
            return self._read(self._RAM_READ,
                              (x1 - x0 + 1) * (y1 - y0 + 1) * size)
        self._write(self._RAM_WRITE, data) 

    def _write(self, command=None, data=None):
        if command is not None:
            self._dc(0)
            self._ili9341_cs(0)
            self._spi.write(bytearray([command]))
            self._ili9341_cs(1)
        if data is not None:
            self._dc(1)
            self._ili9341_cs(0)
            self._spi.write(data)
            self._ili9341_cs(1)

    def _read(self, command=None, count=0):
        self._dc(0)
        self._ili9341_cs(0)
        if command is not None:
            self._spi.write(bytearray([command]))
        if count:
            data = self._spi.read(count)
        self._ili9341_cs(1)
        return data
