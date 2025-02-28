from .PCF8574 import *
from .Adafruit_LCD1602 import Adafruit_CharLCD
from .weather_codes import get_weather_description

mcp = PCF8574_GPIO(0x27)  # Create GPIO adapter
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

def set_lcd(water_level):
    mcp.output(3,1)     # Turn on backlight
    lcd.begin(16,2)     # Initialize 16x2 LCD
    lcd.clear()
    lcd.display()
    lcd.setCursor(0,0)
    lcd.message(f'Erdfeuchtigkeit:\n{water_level}')
    return None
