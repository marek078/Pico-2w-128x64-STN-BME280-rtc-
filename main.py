import machine, time, micropython

from micropyGPS import MicropyGPS

import bme280_i2c
from ds1302 import DS1302
from st7920 import ST7920
import framebuf2 as framebuf
ds = DS1302(machine.Pin(0),machine.Pin(5),machine.Pin(4)) # pini pre hodiny rtc

#print(ds.date_time()) # returns the current datetime.


#ds.date_time([2025, 3, 5, 3, 15, 54,30  ]) # set datetime. ## nastavit cas pre RTC 0 je sunday


#(Y,M,D,day,hr,m,s)=ds.date_time()

#ds.hour() # returns hour.
#print(ds.date_time())

#init pre GPS
gps = MicropyGPS(+2) # local ofset +2 
gps_serial = machine.UART(0, baudrate=9600, tx=machine.Pin(12), rx=machine.Pin(13))


def GPS():   
    data = gps_serial.read()
    for byte in data:
        stat = gps.update(chr(byte))
        if stat is not None: 
            print('UTC Timestamp:', gps.timestamp)
            print('Date:', gps.date_string('long'))
            print('Latitude:', gps.latitude_string())
            print('Longitude:', gps.longitude_string())
            print('Altitude:', gps.altitude)
            print('Satellites in use:', gps.satellites_in_use)
            print('Horizontal Dilution of Precision:', gps.hdop)
                
            return (gps.date_string('short'), gps.timestamp, gps.latitude_string(),
                  gps.longitude_string(), gps.altitude, '{:02.2f}'.format(gps.speed[2]))
            
            
# pini pre display
# pin_spi = 18
# pin_mosi = 19
# pin_cs = 17

# init display
spi = machine.SPI(0, baudrate=800000, sck=machine.Pin(18), mosi=machine.Pin(19))
cs = machine.Pin(17, machine.Pin.OUT, value=0)
fbuf = ST7920(spi, cs)

print(fbuf._spi)

fbuf_gps = framebuf.FrameBuffer(bytearray(128*64 // 2), 128, 64,framebuf.MONO_HLSB) # pre gps rýchlosť

def vip(data): #vykreslovanie-------
    fbuf.fill(0)
    fbuf.rect(0,0,128,64,0xffff)
    fbuf.text(data[0], 3, 31,0xffff)
    fbuf.text(str(rtc.datetime()[2])+'.'+'0'+str(rtc.datetime()[1]),3,3,0xffff) 
    fbuf.text(data[1], 3, 13, 0xffff)
    fbuf.text(data[2], 3, 22, 0xffff)
    fbuf.text(data[3], 60, 3, 0xffff)
    fbuf.text('N',100,41,0xffff)
    fbuf.text('E',100,51,0xffff)
    fbuf.text( data[4], 3, 41,0xffff)
    fbuf.text(data[5], 3, 51,0xffff)
    fbuf.show()


# init pre bme280
i2c = machine.I2C(1, scl=machine.Pin(3), sda= machine.Pin(2), freq=400000 )
sensor = bme280_i2c.BME280_I2C(address=bme280_i2c.BME280_I2C_ADDR_PRIM, i2c=i2c)

sensor.set_measurement_settings({
    'filter': bme280_i2c.BME280_FILTER_COEFF_16,
    'standby_time': bme280_i2c.BME280_STANDBY_TIME_500_US,
    'filter': bme280_i2c.BME280_FILTER_COEFF_OFF,
    'osr_h': bme280_i2c.BME280_OVERSAMPLING_1X,
    'osr_p': bme280_i2c.BME280_OVERSAMPLING_2X,
    'osr_t': bme280_i2c.BME280_OVERSAMPLING_1X})

sensor.set_power_mode(bme280_i2c.BME280_NORMAL_MODE)



rtc = machine.RTC()# hodini
rtc_e = ds.date_time() # externe rtc
rtc.datetime(ds.date_time()+ [0])
#rtc.datetime((rtc_e[0],rtc_e[1],rtc_e[2],0,rtc_e[4],rtc_e[5],rtc_e[6],0))



def main(c):

    print(ds.date_time(),'**')

    print(rtc.datetime()[6])
    
    #time.sleep_ms(70) 
    print(sensor.get_measurement())
    
    t, p , h = sensor.get_measurement()
    
    date, gcas, lat, lot, alt, spd = GPS()
    
    vip( ('t{:+05.1f}C'.format(t), 'h{:02.0f}%'.format(h) , 'p{:04d}'.format(p // 100)       #nechitať
          ,'{:02d}:{:02d}:{:02d}'.format(rtc.datetime()[4], rtc.datetime()[5], rtc.datetime()[6]) 
          ,lat,lot))
   
    print(lat,lot)
    print(alt)
    print(gcas)
    
cas = machine.Timer() #casovac
cas.init(period=1000, callback=main) #1000ms
