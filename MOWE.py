from OmegaExpansion import onionI2C

import time
import os

# Get I2C bus

i2c = onionI2C.OnionI2C()
# BMP280 address, 0x76(118)
# Read data back from 0x88(136), 24 bytes
b1 = i2c.readBytes(0x76, 0x88, 25)

# Convert the data

# Temp coefficents
dig_T1 = b1[1] * 256 + b1[0]
dig_T2 = b1[3] * 256 + b1[2]
if dig_T2 > 32767 :
    dig_T2 -= 65536
dig_T3 = b1[5] * 256 + b1[4]
if dig_T3 > 32767 :
    dig_T3 -= 65536

# Pressure coefficents
dig_P1 = b1[7] * 256 + b1[6]
dig_P2 = b1[9] * 256 + b1[8]
if dig_P2 > 32767 :
    dig_P2 -= 65536
dig_P3 = b1[11] * 256 + b1[10]
if dig_P3 > 32767 :
    dig_P3 -= 65536
dig_P4 = b1[13] * 256 + b1[12]
if dig_P4 > 32767 :
    dig_P4 -= 65536
dig_P5 = b1[15] * 256 + b1[14]
if dig_P5 > 32767 :
    dig_P5 -= 65536
dig_P6 = b1[17] * 256 + b1[16]
if dig_P6 > 32767 :
    dig_P6 -= 65536
dig_P7 = b1[19] * 256 + b1[18]
if dig_P7 > 32767 :
    dig_P7 -= 65536
dig_P8 = b1[21] * 256 + b1[20]
if dig_P8 > 32767 :
    dig_P8 -= 65536
dig_P9 = b1[23] * 256 + b1[22]
if dig_P9 > 32767 :
    dig_P9 -= 65536

# BMP280 address, 0x76(118)
# Read data back from 0x88(136), 24 bytes
b2 = i2c.readBytes(0x76, 0xA1, 15)

# Hum coefficents
dig_H1 =  b2[1] * 256 + b2[0]
dig_H2 =  b2[3] * 256 + b2[2]
if dig_H2 > 32767 :
    dig_H2 -= 65536
dig_H3 =  b2[5] * 256 + b2[4]
if dig_H3 > 32767 :
    dig_H3 -= 65536
dig_H4 =  b2[7] * 256 + b2[6]
if dig_H4 > 32767 :
    dig_H4 -= 65536
dig_H5 =  b2[9] * 256 + b2[8]
if dig_H5 > 32767 :
    dig_H5 -= 65536
dig_H6 =  b2[11] * 256 + b2[10]
if dig_H6 > 32767 :
    dig_H6 -= 65536
dig_H7 =  b2[13] * 256 + b2[12]
if dig_H7 > 32767 :
    dig_H7 -= 65536





# BMP280 address, 0x76(118)
# Select Control measurement register, 0xF4(244)
#               0x27(39)        Pressure and Temperature Oversampling rate = 1
#                                       Normal mode
i2c.writeByte(0x76, 0xF4, 0x27)
# BMP280 address, 0x76(118)
# Select Configuration register, 0xF5(245)
#               0xA0(00)        Stand_by time = 1000 ms
i2c.writeByte(0x76, 0xF5, 0xA0)

i2c.writeByte (0x76, 0xF2, 0x01)
time.sleep(0.5)

# BMP280 address, 0x76(118)
# Read data back from 0xF7(247), 8 bytes
# Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
# Temperature xLSB, Humidity MSB, Humidity LSB
data = i2c.readBytes(0x76, 0xF7,9 )
# Convert pressure and temperature data to 19-bits
adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16
adc_H = ((data[6] * 65536) + (data[7] * 256) + (data[8] & 0xF0)) / 16

# Humidity offset calculations
#var_H = ((t_fine)  - 76800.0);
#var_H = (adc_H  - (dig_H4) * 64.0 + (dig_H5 / 16384.0 * var_H))*((dig_H2) / 65536.0 * (1.0 + (dig_H6) / 67108864.0 * var_H *
#(1.0 + (dig_H3) / 67108864.0 * var_H)));
#var_H = var_H * (1.0 - (dig_H1) * var_H / 524288.0);
#Humi = var_H/1024


# Temperature offset calculations
var1 = ((adc_t) / 16384.0 - (dig_T1) / 1024.0) * (dig_T2)
var2 = (((adc_t) / 131072.0 - (dig_T1) / 8192.0) * ((adc_t)/131072.0 - (dig_T1)/8192.0)) * (dig_T3)
t_fine = (var1 + var2)
cTemp = (var1 + var2) / 5120.0
fTemp = cTemp * 1.8 + 32

# Pressure offset calculations
var1 = (t_fine / 2.0) - 64000.0
var2 = var1 * var1 * (dig_P6) / 32768.0
var2 = var2 + var1 * (dig_P5) * 2.0
var2 = (var2 / 4.0) + ((dig_P4) * 65536.0)
var1 = ((dig_P3) * var1 * var1 / 524288.0 + ( dig_P2) * var1) / 524288.0
var1 = (1.0 + var1 / 32768.0) * (dig_P1)
p = 1048576.0 - adc_p
p = (p - (var2 / 4096.0)) * 6250.0 / var1
var1 = (dig_P9) * p * p / 2147483648.0
var2 = p * (dig_P8) / 32768.0
pressure = (p + (var1 + var2 + (dig_P7)) / 16.0) / 100


# Humidity offset calculations
var_H = ((t_fine)  - 76800.0);
var_H = (adc_H  - (dig_H4) * 64.0 + (dig_H5 / 16384.0 * var_H))*((dig_H2) / 65536.0 * (1.0 + (dig_H6) / 67108864.0 * var_H *
(1.0 + (dig_H3) / 67108864.0 * var_H)));
var_H = var_H * (1.0 - (dig_H1) * var_H / 524288.0);
Humi = var_H/1024

#Print data
print "Tlak : %.2f hPa " %pressure
print "Teplota : %.2f C" %cTemp
print "Teplota ve Fairhaint : %.2f F" %fTemp

os.system ('curl "https://divecky.com/ap/input.php?device=999&tempout=%.2f"'%cTemp)



#import json
#import requests

#url = "https://divecky.com/ap/input.php?device=998&tempout=%.2f&bar=%.2f" % (cTemp, pressure)
#data = requests.get(url).json


time.sleep (30)