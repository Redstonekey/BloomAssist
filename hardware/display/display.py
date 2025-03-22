from .fake_lcd import FakePCF8574_GPIO, FakeAdafruit_CharLCD #fake
from datetime import datetime
import time
from .PCF8574 import PCF8574_I2C, PCF8574_GPIO
from .Adafruit_LCD1602 import Adafruit_CharLCD  #real
mcp_fake = FakePCF8574_GPIO(0x27)  # Create fake GPIO adapter
lcd_fake = FakeAdafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp_fake) #fake


try:
    mcp = PCF8574_GPIO(0x27)  # type: ignore # Create GPIO adapter #real
    lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp) # type: ignore #real
except Exception as e:
    print(e)

def get_time_now():     # get system time
    return datetime.now().strftime('    %H:%M:%S')



def set_lcd(water_level, water_level_n):
    print(f'{water_level}   {water_level_n}')
    start_time = datetime.now()
    mcp.output(3,1)     # Turn on backlight
    lcd.begin(16,2)     # Initialize 16x2 LCD
    lcd.clear()
    lcd.display()
    lcd.setCursor(0,0)
    lcd.message(f'Erdfeuchtigkeit:\n{water_level}')
    if water_level_n >= 10:
        print('10!!!!')
        lcd.setCursor(11,1)
    else:
        lcd.setCursor(12,1)  # Position cursor at column 12, row 1 (second line)
    lcd.message(f'{water_level_n}/10')

def set_test_lcd(water_level, water_level_n):
    print(f'{water_level}   {water_level_n}')
    start_time = datetime.now()
    mcp_fake.output(3,1)     # Turn on backlight
    lcd_fake.begin(16,2)     # Initialize 16x2 LCD
    lcd_fake.clear()
    lcd_fake.display()
    lcd_fake.setCursor(0,0)
    lcd_fake.message(f'Erdfeuchtigkeit:\n{water_level}')
    if water_level_n >= 10:
        print('10!!!!')
        lcd_fake.setCursor(11,1)
    else:
        lcd_fake.setCursor(12,1)  # Position cursor at column 12, row 1 (second line)
    lcd_fake.message(f'{water_level_n}/10')