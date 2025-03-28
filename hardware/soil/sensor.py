import spidev  # type: ignore
AIR_VALUE = 1023   # Value when sensor is in air
WATER_VALUE = 633 # Value when sensor is in water

# SPI setup
spi = spidev.SpiDev() # type: ignore
spi.open(0, 0)  # Open SPI bus 0, device (CS) 0
spi.max_speed_hz = 1350000


def soil_moisture_level(sensor_value):
    # Calculate scale from 1-10 based on sensor range
    scale = round(10 - ((sensor_value - WATER_VALUE) / (AIR_VALUE - WATER_VALUE) * 9))
    # Ensure scale stays within 1-10 range
    scale = max(1, min(10, scale))
    
    # Original text-based status
    if sensor_value >= 1023:
        return "Sehr Trocken", scale
    elif 900 <= sensor_value < 1023:
        return "Trocken", scale
    elif 750 <= sensor_value < 900:
        return "Feucht", scale
    elif 634 <= sensor_value < 750:
        return "Sehr feucht", scale
    elif sensor_value <= 633:
        return "Nass", scale
    else:
        return "ERROR 301", 0



def read_adc(channel):
    """Read SPI data from MCP3008, 8 channels [0-7]."""
    if channel < 0 or channel > 7:
        return -1
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# try:
#     while True:
#         # Read from channel 0 (where the sensor is connected)
#         adc_value = read_adc(0)
#         moisture_status = soil_moisture_level(adc_value)

#         print(f" {adc_value} | {moisture_status}")

#         time.sleep(1)

# except KeyboardInterrupt:
#     spi.close()
#     print("\nProgram terminated.")



def get_water_level():
    adc_value = read_adc(0)
    moisture_status = soil_moisture_level(adc_value)
    return moisture_status
# def get_test_level():
#     moisture_status = soil_moisture_level(700)
#     return moisture_status
