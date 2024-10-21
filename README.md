# Real-time Data Collection and Transmission

This project involves collecting real-time data from MPU-9250/6500 sensors and transmitting it to Firebase for storage and analysis.

## Table of Contents
- [Description](#description)
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [License](#license)

## Description
This Python script collects accelerometer and gyroscope data from an MPU-9250/6500 sensor and calculates a PDI (Performance Degradation Index) based on the data. The script also integrates GPS data and pushes the collected data to a Firebase database.

## Features
- Real-time data collection from MPU-9250/6500 sensors
- GPS data integration
- Firebase database connectivity
- Multithreading for concurrent data collection and transmission

## Setup

1. Install the required Python libraries.
   pip install matplotlib
   sudo apt-get install python3-smbus
   pip install pyrebase4
   pip install pyserial
2. Update the config dictionary with your Firebase project credentials.
3. Ensure the MPU-9250/6500 sensor is connected to the I2C bus.
4. Connect the GPS module to the specified serial port.

## Usage 
Run the script
   python detector.py
## License
This project is licensed under an "All Rights Reserved" License. All rights to the SmoothRide application and its source code are owned by Ritesh Aukhojee. Any unauthorized use, distribution, or modification of the code is strictly prohibited. For any inquiries, please contact riteshaukhojee01@gmail.com.
   
   
