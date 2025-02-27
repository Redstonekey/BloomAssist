from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from time import sleep
import requests
from weather_codes import get_weather_description

def get_weather():
    city = "Heusenstamm"
    api_key = "f7bc51e1e5c3488d960162419252402"
    weather_api_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"  
    response_weather = requests.get(weather_api_url)
    if response_weather.status_code != 200:
        return None, None
    weather_data = response_weather.json()
    if "current" in weather_data:
        temperature = weather_data["current"]["temp_c"]
        weather_code = weather_data["current"]["condition"]["code"]
        weather_description = get_weather_description(weather_code)
        return temperature, weather_description
    else:
        return None, None

# Beispielaufruf der Funktion
temperature, weather_description = get_weather()

mcp = PCF8574_GPIO(0x27)  # Create GPIO adapter
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

def loop():
    while True:
        lcd.clear()
        lcd.setCursor(0,0)
        temp, weather = get_weather()
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.message(f'Temperatur: {temp}°C')
        lcd.setCursor(0,1)  # Move to second line
        lcd.message(f'Wetter: {weather}')
        sleep(10)
        lcd.clear()
        lcd.setCursor(0,0)
        lcd.message("Präsentiert von\nBloom Assist")
        sleep(10)


        def run_with_retry():
            try:
                loop()
            except:
                sleep(1)
                run_with_retry()


if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        mcp.output(3,1)     # Turn on backlight
        lcd.begin(16,2)     # Initialize 16x2 LCD
        lcd.display()
        loop()
    except KeyboardInterrupt:
        lcd.clear()
        lcd.noDisplay()
        print ('Program stopped')