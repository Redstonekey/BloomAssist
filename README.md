# BloomAssist

BloomAssist is a smart plant monitoring and care assistant that combines hardware sensors with an AI-powered web interface to help users take better care of their plants.

## Features

- **Plant Identification**: Upload images to automatically identify plants using PlantNet API
- **Moisture Monitoring**: Real-time soil moisture tracking using hardware sensors
- **AI Chat Assistant**: Get plant care advice from an AI powered by Google's Gemini model
- **Data Visualization**: Track moisture levels and plant health over time
- **Smart Notifications**: Receive alerts about watering and care needs
- **LCD Display**: Hardware interface showing current moisture levels
- **Multi-User Support**: Individual accounts with personalized plant collections

## Hardware Components

- Soil moisture sensor connected via SPI
- 16x2 LCD display (PCF8574/I2C)
- Raspberry Pi (recommended) for running the system

## Software Requirements

- Python 3.10+
- Flask web framework
- SQLite database
- Required Python packages:
  ```sh
  pip install flask google-generativeai pillow requests schedule