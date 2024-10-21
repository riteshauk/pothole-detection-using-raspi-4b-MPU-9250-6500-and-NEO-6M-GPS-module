import smbus
import time
import matplotlib.pyplot as plt
import math
import pyrebase
import threading
import serial


# Constants
k1 = 8.519548561619565e-05
k2 = 0.0013891767789282249
LONGITUDE = 0
LATITUDE = 0

# Firebase configuration
config = {
 "apiKey": "AIzaSyDv9aVCAK3QfpyZPsRzekJlc3MsBfZoxrg",
  "authDomain": "test-f6ef2.firebaseapp.com",
  "databaseURL": "https://test-f6ef2-default-rtdb.firebaseio.com",
 "projectId": "test-f6ef2",
  "storageBucket": "test-f6ef2.appspot.com",
  "messagingSenderId": "148456236172",
  "appId": "1:148456236172:web:8a09751c0fd0a1a76f47a9",
  "measurementId": "G-MX40KYM5YS"
}
def push_user_to_firebase(longitude, latitude, pdi, config):
    print("sending")
    # Initialize the Firebase app with the given configuration
    firebase = pyrebase.initialize_app(config)

    # Get a reference to the database service
    database = firebase.database()

    # Check if the same name and age combination already exists
    users = database.child('users').get()
    if users.each():
        for user in users.each():
            user_data = user.val()
            if user_data['longitude'] == longitude and user_data['latitude'] == latitude:
                if user_data['pdi'] == pdi:
                    print("Data with the same name, age, and class already exists. Not pushing to the database.")
                    return
                else:
                    # Update the existing record with the new class
                    database.child('users').child(user.key()).update({'pdi': pdi})
                    print("Data updated in the database.")
                    return

    # If name and age combination does not exist, push the data to the 'users' node
    data = {
        'longitude': longitude,
        'latitude': latitude,
        'pdi': pdi
    }

    database.child('users').push(data)
    print("Data pushed to the database.")



def calculate_pdi(zacc, xgyro, ygyro):
        # Ensure the value inside sqrt is non-negative
        global k1,k2
        return math.sqrt(max(0, zacc**2 + k1 * xgyro**2 + k2 * ygyro**2))
def read_mpu_data():
    # I2C address of the MPU-9250/6500
    MPU_ADDR = 0x68

    # Accelerometer and gyroscope registers
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43

    # Scaling factors
    ACCEL_SCALE = 16384.0  # for Â±2g range
    GYRO_SCALE = 131.0      # for Â±250Â°/s range

    # Initialize I2C bus
    bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1

    # Wake up the MPU-9250/6500 (it starts in sleep mode)
    bus.write_byte_data(MPU_ADDR, 0x6B, 0)

    def read_word(reg):
        high = bus.read_byte_data(MPU_ADDR, reg)
        low = bus.read_byte_data(MPU_ADDR, reg + 1)
        value = (high << 8) + low
        if value >= 0x8000:  # handle negative values
            value = -((65535 - value) + 1)
        return value

#     plt.ion()  # Turn on interactive mode
#     fig, ax = plt.subplots()
#     x_vals = []
#     z_accel_vals = []
#     x_gyro_vals = []
    maxindex = 0
    c=1
    while True:
        if c==1:
            t1 = time.time()
            c=0
        # Read accelerometer data
        accelX = read_word(ACCEL_XOUT_H)
        accelY = read_word(ACCEL_XOUT_H + 2)
        accelZ = read_word(ACCEL_XOUT_H + 4)

        # Read gyroscope data
        gyroX = read_word(GYRO_XOUT_H)
        gyroY = read_word(GYRO_XOUT_H + 2)
        gyroZ = read_word(GYRO_XOUT_H + 4)

        # Convert raw data to physical units
        accelZ_g = accelZ / ACCEL_SCALE
        gyroX_dps = gyroX / GYRO_SCALE
        gyroY_dps = gyroY / GYRO_SCALE

#         # Append data to lists
#         x_vals.append(len(x_vals))
#         z_accel_vals.append(accelZ_g)
#        # x_gyro_vals.append(gyroX_dps)


        # Update the plot
#         ax.clear()
#         ax.plot(x_vals, z_accel_vals, label='Z Acceleration (g)')
#         ax.plot(x_vals, x_gyro_vals, label='X Gyroscope (Â°/s)')
#         ax.legend()
# 
#         plt.pause(0.05)  # Pause to allow the plot to update
        time.sleep(0.05)  # delay of 50ms
        
        index = round((calculate_pdi(accelZ_g,gyroX_dps,gyroY_dps)-1)*4)
        t2 = time.time()
        if index>maxindex:
            maxindex = index
        if t2-t1>0.5:
            print(maxindex,LONGITUDE,LATITUDE)
            if maxindex>=2:
                push_user_to_firebase(LONGITUDE, LATITUDE, maxindex, config)
            maxindex=0
            c=1


#     plt.ioff()  # Turn off interactive mode

# Call the method to read and plot MPU data
#read_mpu_data()

def read_gps():
    global LONGITUDE
    global LATITUDE
    while True:
        port = "/dev/ttyAMA0"
        ser = serial.Serial(port, baudrate=9600, timeout=0.5)
        newdata = ser.readline()

        # Decode the line from bytes to string, replacing invalid bytes with a replacement character
        newdata = newdata.decode('utf-8', errors='replace').strip()


        # Check if the line is a GNRMC sentence
        if newdata.startswith('$GNRMC'):
            # Split the sentence into fields
            fields = newdata.split(',')

            # Extract the latitude and longitude fields
            lat_field = fields[3]
            lon_field = fields[5]

            # Extract the latitude direction (N/S)
            lat_dir = fields[4]

            # Extract the longitude direction (E/W)
            lon_dir = fields[6]

            # Convert the latitude and longitude fields to decimal degrees
            if len(lat_field) >= 2:
                lat_deg = int(lat_field[:2]) + float(lat_field[2:]) / 60
                if lat_dir == 'S':
                    lat_deg = -lat_deg
                lon_deg = int(lon_field[:3]) + float(lon_field[3:]) / 60
                if lon_dir == 'W':
                    lon_deg = -lon_deg

                # Print the latitude and longitude
                #print(f"Latitude: {lat_deg:.6f}, Longitude: {lon_deg:.6f}")
                LONGITUDE = lon_deg
                LATITUDE = lat_deg
    




readthread = threading.Thread(target=read_mpu_data)
readgps = threading.Thread(target=read_gps)
readthread.start()
readgps.start()
readgps.join()
readthread.join()
