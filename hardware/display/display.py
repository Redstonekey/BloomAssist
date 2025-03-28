from .fake_lcd import FakePCF8574_GPIO, FakeAdafruit_CharLCD
from datetime import datetime
import time

# Initialize variables at module level
mcp = None
lcd = None
USE_TEST_MODE = False
mcp_fake = FakePCF8574_GPIO(0x27)
lcd_fake = FakeAdafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp_fake)

def init_hardware():
    global mcp, lcd, USE_TEST_MODE
    try:
        from .PCF8574 import PCF8574_I2C, PCF8574_GPIO
        from .Adafruit_LCD1602 import Adafruit_CharLCD
        
        mcp = PCF8574_GPIO(0x27)
        lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
        USE_TEST_MODE = False
        print("Hardware initialization successful")
        return True
    except (ImportError, Exception) as e:
        print(f"Hardware initialization failed: {e}")
        USE_TEST_MODE = True
        return False

def get_time_now():
    return datetime.now().strftime('    %H:%M:%S')

def set_lcd(water_level, water_level_n):
    init_hardware()
    global USE_TEST_MODE
    print(f'{water_level}   {water_level_n}')
    
    if not USE_TEST_MODE and mcp and lcd:
        try:
            mcp.output(3,1)
            lcd.begin(16,2)
            lcd.clear()
            lcd.display()
            lcd.setCursor(0,0)
            lcd.message(f'Erdfeuchtigkeit:\n{water_level}')
            if water_level_n >= 10:
                lcd.setCursor(11,1)
            else:
                lcd.setCursor(12,1)
            lcd.message(f'{water_level_n}/10')
        except Exception as e:
            print(f"Error using real hardware: {e}")
            USE_TEST_MODE = True
            set_test_lcd(water_level, water_level_n)
    else:
        set_test_lcd(water_level, water_level_n)

def set_test_lcd(water_level, water_level_n):
    print(f'TEST MODE: {water_level}   {water_level_n}')
    try:
        mcp_fake.output(3,1)
        lcd_fake.begin(16,2)
        lcd_fake.clear()
        lcd_fake.display()
        lcd_fake.setCursor(0,0)
        lcd_fake.message(f'Erdfeuchtigkeit:\n{water_level}')
        if water_level_n >= 10:
            lcd_fake.setCursor(11,1)
        else:
            lcd_fake.setCursor(12,1)
        lcd_fake.message(f'{water_level_n}/10')
    except Exception as e:
        print(f"Error in test mode: {e}")

# Initialize hardware when module is loaded
init_hardware()