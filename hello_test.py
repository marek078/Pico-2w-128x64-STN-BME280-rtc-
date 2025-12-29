# imports
from machine import SPI, Pin
from st7920 import ST7920
import utime

# define pins
pin_spi = 18
pin_mosi = 19
pin_cs = 17

# init
spi = SPI(0, baudrate=100000, sck=Pin(pin_spi), mosi=Pin(pin_mosi))
cs = Pin(pin_cs, Pin.OUT, value=0)
fbuf = ST7920(spi, cs)

# print spi info
print(fbuf._spi)

# display stuff
fbuf.fill(0)

while True:
   fbuf.rect(0,0,128,64,0x0000,True)
   fbuf.text('Hello', 0, 0, 0xffff)
   fbuf.text('RASPBER PI PICO', 0, 16, 0xffff)
   fbuf.text('ISMAIL BASIC', 0, 32, 0xffff)
   fbuf.text('ISMAIL BASIC', 0, 48, 0xffff)
   fbuf.show()
   
   
   
#    fbuf.text('Hello World!', 0, 0, 0x0000)
#    fbuf.text('RASPBER PI PICO', 0, 16, 0x0000)
#    fbuf.text('ISMAIL BASIC', 0, 32, 0x0000)
#    fbuf.text('ISMAIL BASIC', 0, 48, 0x0000)
#    fbuf.show()
   
   
