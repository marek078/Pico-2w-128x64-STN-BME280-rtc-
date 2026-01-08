import machine, time, micropython

from micropyGPS import MicropyGPS

import bme280_i2c
from ds1302 import DS1302
from st7920 import ST7920
import framebuf2 as framebuf

#init pre hodiny
ds = DS1302(machine.Pin(0),machine.Pin(5),machine.Pin(4)) # pini pre hodiny rtc

#print(ds.date_time()) # returns the current datetime.
#ds.date_time([2025, 3, 5, 3, 15, 54,30  ]) # set datetime. ## nastavit cas pre RTC 0 je sunday
#(Y,M,D,day,hr,m,s)=ds.date_time()
#ds.hour() # returns hour.
#print(ds.date_time())


rtc = machine.RTC()# hodiny
rtc.datetime(ds.date_time()+[0])
#rtc.datetime((rtc_e[0],rtc_e[1],rtc_e[2],0,rtc_e[4],rtc_e[5],rtc_e[6],0))


#init pre GPS
gps = MicropyGPS(+2) # local ofset +2 
gps_serial = machine.UART(0, baudrate=9600, tx=machine.Pin(12), rx=machine.Pin(13))


def GPS():   
    data = gps_serial.read()
    for byte in data:
        stat = gps.update(chr(byte))
        if stat is not None: 
#             print('UTC Timestamp:', gps.timestamp)
#             print('Date:', gps.date_string('long'))
#             print('Latitude:', gps.latitude_string())
#             print('Longitude:', gps.longitude_string())
#             print('Altitude:', gps.altitude)
#             print('Satellites in use:', gps.satellites_in_use)
#             print('Horizontal Dilution of Precision:', gps.hdop)
                
            return (gps.date_string('short'), gps.timestamp, gps.latitude_string(),
                  gps.longitude_string(), gps.altitude, '{:02.2f}'.format(gps.speed[2]))
            
# init pre display         
# pini pre display
# pin_spi = 18
# pin_mosi = 19
# pin_cs = 17

spi = machine.SPI(0, baudrate=800000, sck=machine.Pin(18), mosi=machine.Pin(19))
cs = machine.Pin(17, machine.Pin.OUT, value=0)
fbuf = ST7920(spi, cs)


#fbuf_test =framebuf.FrameBuffer(bytearray(128*64 // 2), 20, 20,framebuf.MONO_HLSB)
fbuf_sensor = framebuf.FrameBuffer(bytearray(312), 60, 39,framebuf.MONO_HLSB) #60*39 = 2 340 pocet pixelov / 8  = 292,5 pocet potrebných bajtov
fbuf_avg = framebuf.FrameBuffer(bytearray(40), 23, 10,framebuf.MONO_HLSB) 
fbuf_min = framebuf.FrameBuffer(bytearray(40), 23, 10,framebuf.MONO_HLSB)
fbuf_max = framebuf.FrameBuffer(bytearray(40), 23, 10,framebuf.MONO_HLSB)
fbuf_time = framebuf.FrameBuffer(bytearray(80), 64 ,10 ,framebuf.MONO_HLSB)
fbuf_date = framebuf.FrameBuffer(bytearray(40), 30, 10,framebuf.MONO_HLSB) # rok dlzka !!!!
fbuf_gps = framebuf.FrameBuffer(bytearray(312), 124, 19,framebuf.MONO_HLSB) 
 

def vip(data): #vykreslovanie-------
    fbuf.fill(0)
    fbuf_sensor.fill(0)
    fbuf_min.fill(0) 
    fbuf_max.fill(0) 
    fbuf_avg.fill(0)
    fbuf_time.fill(0)
    fbuf_date.fill(0)
    fbuf_gps.fill(0)
    fbuf.rect(0,0,128,64,1)
    
    fbuf_sensor.text(data[0], 0, 18,1)
    fbuf_sensor.text(data[1], 0, 0, 1)
    fbuf_sensor.text(data[2], 0, 9, 1)
    
    fbuf_min.text(data[6],0,0,1)
    fbuf_avg.text(data[5],0,0,1)
    fbuf_max.text(data[7],0,0,1)
    
    
    fbuf_time.text(data[3], 0, 3, 1)
    fbuf_date.text(data[4],0,3,1)
    
    fbuf_gps.text('N',100,0,1)
    fbuf_gps.text('E',100,9,1)
    fbuf_gps.text( data[8], 3, 0,1)
    fbuf_gps.text(data[9], 3, 9,1)
    
    fbuf.blit(fbuf_sensor,3,15)
    fbuf.blit(fbuf_min,53,33)
    fbuf.blit(fbuf_max,101,33)
    fbuf.blit(fbuf_avg,77,33)
    fbuf.blit(fbuf_time,58,2)
    fbuf.blit(fbuf_date,3,2)
    fbuf.blit(fbuf_gps,3,44)
    
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


            
f_avg  = 0
Minmaxi = (0,0)
def avg(i):
    global f_avg , Minmaxi
    f_plus = 0
    if len(i) == 60:
        for f in i:
            f_plus += f
        f_avg = f_plus / 60
        Minmaxi = min(i) , max(i)
        del i[0]
    return (f_avg)
      
    
def debug():
    print('hodinyD',ds.date_time(),'**')
    print('hodinyS:',rtc.datetime()[6])
    print('display_nastavenie:',fbuf._spi)
    print('senzor:',sensor.get_measurement())
    print('avg_len:',len(avg_t))
    print(micropython.mem_info())


avg_t = []
avg_p = []
avg_h = []
def main(c):
    
    t, p , h = sensor.get_measurement()
    avg_t.append(t) 
    #'{:+0.0f}'.format(avg(avg_t)[1[0]]) , '{:+0.0f}'.format(avg(avg_t)[1][0])
    Y, M, D, Day, hr, m, s, ms = rtc.datetime()
    date, gcas, lat, lot, alt, spd = GPS() # pridať try

    vip( ('t{:+05.1f}'.format(t), 'h{:02.0f}%'.format(h) , 'p{:04d}'.format(p // 100)    #nechitať
          ,'{:02d}:{:02d}:{:02d}'.format(hr, m, s) , '{}.{}'.format(D,M), '{:+0.0f}'.format(avg(avg_t)), '{:+0.0f}'.format(Minmaxi[0]), '{:+0.0f}'.format(Minmaxi[1])
          ,lat,lot))
    debug()
cas = machine.Timer() #casovac
cas.init(period=1000, callback=main) #1000ms
