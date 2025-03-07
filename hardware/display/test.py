from fake_lcd import FakePCF8574_GPIO, FakeAdafruit_CharLCD
from datetime import datetime
import time

mcp = FakePCF8574_GPIO(0x27)  # Create fake GPIO adapter
lcd = FakeAdafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)

def get_time_now():
    return datetime.now().strftime('  %H:%M:%S')

def set_lcd(water_level, water_level_n):
    print(f'{water_level}   {water_level_n}')
    start_time = datetime.now()
    mcp.output(3, 1)  # Turn on backlight (fake)
    lcd.begin(16, 2)  # Initialize 16x2 LCD (fake)
    lcd.clear()
    lcd.display()
    lcd.setCursor(0, 0)
    lcd.message(f'Erdfeuchtigkeit:\n{water_level}')
    if water_level_n >= 10:
        print('10!!!!')
        lcd.setCursor(11, 1)
    else:
        lcd.setCursor(12, 1)  # Position cursor at column 12, row 1 (second line)
    lcd.message(f'{water_level_n}/10')