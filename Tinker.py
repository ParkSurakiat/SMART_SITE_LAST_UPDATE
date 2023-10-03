import cv2
import time
import datetime
import serial
import subprocess
import smbus2 as smbus
import json 
import paho.mqtt.client as mqtt
# import modbus_tk
# import modbus_tk.defines as cst
# from modbus_tk import modbus_rtu

import threading
import os
import psutil
import random

with open('Count_data.json', 'r') as openfile:
    # Reading from json file
    json_object = json.load(openfile)

write_data_COUNT = json_object

site_code = write_data_COUNT["site_code"]
count_of_slave = write_data_COUNT["count_of_slave"]
count_cabinets = write_data_COUNT["count_cabinets"]
deviceName = write_data_COUNT["deviceName"]
ip_address = write_data_COUNT["ip_address"]
alarm_timer = write_data_COUNT["alarm_timer"]

# cvlc v4l2:///dev/video5 --sout '#transcode{vcodec=h264,acodec=none}:rtp{sdp=rtsp://:8554/}'

# กำหนด URL ของกล้องผ่าน RTSP
rtsp_url = "rtsp://192.168.11.104:8554/"

# เปิดการเชื่อมต่อกับกล้อง
cap = cv2.VideoCapture(rtsp_url)

# กำหนดขนาดของวิดีโอ
frame_width = 640
frame_height = 480
frame_rate = 15

#ที่อยู่ของ mp4 และ video ที่ถูกบันทึก
output_mp4AndJpg_path = '/home/linaro/AIS_PARK_NEW/Photo_and_Video/'

# กำหนดระยะเวลาหน่วงระหว่างการบันทึก snapshot (วินาที)
snapshot_interval_P1 = 1 #ทุกๆ 1 วิ
snapshot_interval_P2 = 180 #ทุกๆ 3 นาที
last_snapshot_time = 0
#หัวใจ
last_time_H = 0
Time_interval_H = 8
#GY
last_time_GY = 0
Time_interval_GY = 10
alarm_timer = Time_interval_GY
#Time2Print
last_time_print = 0
Time_interval_print = 2
last_time_print2 = 0
Time_interval_print2 = 2
# #timeMod
last_time_forMod = 0
Time_interval_forMod = 1
# timer emergency
last_time_EMER = 0
time_interval_EMER = 300

### GPIO ###
# Define the GPIO pin number (e.g., GPIO 123)
led_gpio_pin_D = 149
led_gpio_pin_H = 125
led_gpio_pin_GYRO = 146
led_gpio_pin_TCPIP = 123
PIR_gpio_pin = 41
subprocess.run(['gpio', '-g', 'mode', str(led_gpio_pin_D), 'out'])
subprocess.run(['gpio', '-g', 'mode', str(led_gpio_pin_H), 'out'])
subprocess.run(['gpio', '-g', 'mode', str(led_gpio_pin_GYRO), 'out'])
subprocess.run(['gpio', '-g', 'mode', str(led_gpio_pin_TCPIP), 'out'])
subprocess.run(['gpio', '-g', 'mode', str(PIR_gpio_pin), 'in'])

Door_state = 0  # กำหนดสถานะเริ่มต้นของ LED เป็นปิด
subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_D), str(Door_state)])

### I2C ###
# กำหนดหมายเลขของ I2C Bus
bus_number = 7
# กำหนดที่อยู่ของ GY-521
device_address = 0x68  # ที่อยู่เริ่มต้นของ GY-521
i2c_address = 0x40  # ที่อยู่ I2C ของ SHT20

# สร้างออบเจกต์สำหรับ I2C Bus
busGY = smbus.SMBus(bus_number)
busSHT = smbus.SMBus(bus_number)

# กำหนดพื้นที่ที่คุณต้องการให้ SD card ถูกใช้งานไปถึงก่อนที่คุณจะลบข้อมูล (เป็นเปอร์เซ็นต์)
threshold_percent = 70

# ระบุโฟลเดอร์ที่คุณต้องการลบข้อมูลภาพและวิดีโอ
target_folder = '/home/linaro/AIS_PARK_NEW/Photo_and_Video/'

# ตรวจสอบพื้นที่ที่ใช้งานของ SD card
sd_card_usage = psutil.disk_usage('/')


# ส่งคำสั่งให้ GY-521 เปิดใช้งานการวัด
busGY.write_byte_data(device_address, 0x6B, 0)
# อ่านข้อมูลจากเซ็นเซอร์ SHT20
data = busSHT.read_i2c_block_data(i2c_address, 0xE3, 4) 
#OTP
serial_port = serial.Serial('/dev/ttyS0', 115200) 

cap_not_Connect = False

# ตรวจสอบว่าเชื่อมต่อกล้องสำเร็จหรือไม่
if not cap.isOpened():
    print("ไม่สามารถเชื่อมต่อกล้องได้")
    cap_not_Connect = True
    subprocess.run("sudo init 6", shell=True)
    exit()

recording = False
out = None

# กำหนดข้อมูลสำหรับ MQTT Broker
mqtt_broker_address = 'localhost'  # แทนที่ด้วยที่อยู่ของ MQTT Broker ของคุณ

# เชื่อมต่อกับ MQTT Broker
client = mqtt.Client()
client.connect(mqtt_broker_address, 1883)

lock_state = "True"
successL = "True"
messageL = "Lock Successful"
successUL = "False"
messageUL = "Unlock not successful"


while True:
    if cap_not_Connect == True:
        subprocess.run("sudo init 6", shell=True)

    #จังหวะหัวใจเด้อ
    current_time_H = time.time()
    if current_time_H - last_time_H >= Time_interval_H:
        last_time_H = current_time_H  # อัปเดตเวลาของ snapshot ล่าสุด
        subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_H), str(1)])
        print("Heartbeat : 1")
    else:
        current_time_print = time.time()
        if current_time_print - last_time_print >= Time_interval_print and current_time_H - last_time_H < Time_interval_H:
            last_time_print = current_time_print
            subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_H), str(0)])
            print("Heartbeat : 0")

    accel_xout_H = busGY.read_byte_data(device_address, 0x3B)
    accel_xout_L = busGY.read_byte_data(device_address, 0x3C)
    accel_xout = (accel_xout_H << 8) | accel_xout_L

    # อ่านค่าความเร็วแกน Y
    accel_yout_H = busGY.read_byte_data(device_address, 0x3D)
    accel_yout_L = busGY.read_byte_data(device_address, 0x3E)
    accel_yout = (accel_yout_H << 8) | accel_yout_L

    # อ่านค่าความเร็วแกน Z
    accel_zout_H = busGY.read_byte_data(device_address, 0x3F)
    accel_zout_L = busGY.read_byte_data(device_address, 0x40)
    accel_zout = (accel_zout_H << 8) | accel_zout_L

    # อ่านค่าอัตราความเร็วแกน X
    gyro_xout_H = busGY.read_byte_data(device_address, 0x43)
    gyro_xout_L = busGY.read_byte_data(device_address, 0x44)
    gyro_xout = (gyro_xout_H << 8) | gyro_xout_L

    # อ่านค่าอัตราความเร็วแกน Y
    gyro_yout_H = busGY.read_byte_data(device_address, 0x45)
    gyro_yout_L = busGY.read_byte_data(device_address, 0x46)
    gyro_yout = (gyro_yout_H << 8) | gyro_yout_L

    # อ่านค่าอัตราความเร็วแกน Z
    gyro_zout_H = busGY.read_byte_data(device_address, 0x47)
    gyro_zout_L = busGY.read_byte_data(device_address, 0x48)
    gyro_zout = (gyro_zout_H << 8) | gyro_zout_L

    # แปลงค่าให้อยู่ในรูปแบบที่ถูกต้อง (เช่น 2's complement)
    def twos_complement(val, bits):
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val

    # แปลงค่าให้อยู่ในหน่วยที่ถูกต้อง (เช่น g และ deg/s)
    accel_scale = 16384.0  # สำหรับ MPU6000
    gyro_scale = 131.0  # สำหรับ MPU6000

    # ค่าที่ใช้ในการกำหนดข้อความแจ้งเตือน
    threshold_accel = 1.5  # ค่าความเร็วสูงสุดที่ยอมรับในแกน X, Y, และ Z (g)
    threshold_gyro = 150.0  # ค่าอัตราความเร็วสูงสุดที่ยอมรับในแกน X, Y, และ Z (deg/s)

    accel_x = twos_complement(accel_xout, 16) / accel_scale
    accel_y = twos_complement(accel_yout, 16) / accel_scale
    accel_z = twos_complement(accel_zout, 16) / accel_scale

    gyro_x = twos_complement(gyro_xout, 16) / gyro_scale
    gyro_y = twos_complement(gyro_yout, 16) / gyro_scale
    gyro_z = twos_complement(gyro_zout, 16) / gyro_scale

    if abs(accel_x) > threshold_accel or abs(accel_y) > threshold_accel or abs(accel_z) > threshold_accel:
        print("มีการขยับเซ็นเซอร์ในแกนความเร็ว")
        subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_GYRO), str(1)])
        # สร้างเหตุการณ์แจ้งเตือนที่นี่ (เช่น ส่งอีเมล์ หรือแจ้งเตือนผ่านแอพพลิเคชัน)
    else:
        current_time_GY = time.time()
        if current_time_GY - last_time_GY >= Time_interval_GY:
            last_time_GY = current_time_GY  # อัปเดตเวลาของ snapshot ล่าสุด
            subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_GYRO), str(0)])

    if abs(gyro_x) > threshold_gyro or abs(gyro_y) > threshold_gyro or abs(gyro_z) > threshold_gyro:
        subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_GYRO), str(1)])
        print("มีการหมุนเซ็นเซอร์ในแกนอัตราความเร็ว")
        # สร้างเหตุการณ์แจ้งเตือนที่นี่ (เช่น ส่งอีเมล์ หรือแจ้งเตือนผ่านแอพพลิเคชัน)
    else:
        current_time_GY = time.time()
        if current_time_GY - last_time_GY >= Time_interval_GY:
            last_time_GY = current_time_GY 
            subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_GYRO), str(0)])

    # แสดงผลค่า
    current_time_print2 = time.time()
    if current_time_print2 - last_time_print2 >= Time_interval_print2:
        last_time_print2 = current_time_print2
        print("ความเร็วในแกน X (g): {:.2f}".format(accel_x))
        print("ความเร็วในแกน Y (g): {:.2f}".format(accel_y))
        print("ความเร็วในแกน Z (g): {:.2f}".format(accel_z))
        accel_x_rtu = round(accel_x, 2)*100
        accel_y_rtu = round(accel_y, 2)*100
        accel_z_rtu = round(accel_z, 2)*100
        accel_x_json = round(accel_x, 2)
        accel_y_json = round(accel_y, 2)
        accel_z_json = round(accel_z, 2)

        print("อัตราความเร็วในแกน X (deg/s): {:.2f}".format(gyro_x))
        print("อัตราความเร็วในแกน Y (deg/s): {:.2f}".format(gyro_y))
        print("อัตราความเร็วในแกน Z (deg/s): {:.2f}".format(gyro_z))
        gyro_x_rtu = round(gyro_x, 2)*100
        gyro_y_rtu = round(gyro_y, 2)*100
        gyro_z_rtu = round(gyro_z, 2)*100
        gyro_x_json = round(gyro_x, 2)
        gyro_y_json = round(gyro_y, 2)
        gyro_z_json = round(gyro_z, 2)
        print("-" * 20)

    # แปลงข้อมูลเป็นค่าอุณหภูมิ
    raw_temp = (data[0] << 8) + data[1]
    temperature = -46.85 + (175.72 * raw_temp / 65536.0)
    temp_rtu = round(temperature, 2)*100
    temp_json = round(temperature, 2)
    # อ่านข้อมูลความชื้นจากเซ็นเซอร์ SHT20
    data_humidity = busSHT.read_i2c_block_data(i2c_address, 0xE5, 2)

    # แปลงข้อมูลเป็นค่าความชื้น
    raw_humidity = (data_humidity[0] << 8) + data_humidity[1]
    humidity = -6.0 + (125.0 * raw_humidity / 65536.0)
    hum_rtu = round(humidity, 2)*100
    hum_json = round(humidity, 2)
    #PIR_sensor
    # ตรวจสอบสถานะของ push-button
    PIR_state = subprocess.run(['gpio', '-g', 'read', str(PIR_gpio_pin)], capture_output=True, text=True)
    PIR_state = PIR_state.stdout.strip()
    # แสดงผลค่า
    current_time_print = time.time()
    if current_time_print - last_time_print >= Time_interval_print:
        last_time_print = current_time_print
        print("Temperature:", temperature, "°C")
        print("Humidity:", humidity, "%")
        print("PIR_state : ",PIR_state)
    # หากมีการกด push-button


    # อ่านเฟรมภาพจากกล้อง
    ret, frame = cap.read()

    # รับวันที่และเวลาปัจจุบัน
    current_datetime = datetime.datetime.now()
    # แปลงวันที่และเวลาเป็นสตริงแบบกำหนดรูปแบบ
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    #ตัวแปรที่ส่งไป rtu
    cabinet_serf = 21
    cabinet_sers = 188
    cabinet_serc = 2422
    wacthdog_serf = 134
    wacthdog_sers = 557
    otp_serf = 987
    otp_sers = 567
    t_day = current_datetime.strftime("%d")
    t_month = current_datetime.strftime("%m")
    t_years = current_datetime.strftime("%Y")
    t_hour = current_datetime.strftime("%H")
    t_min = current_datetime.strftime("%M")
    t_sec = current_datetime.strftime("%S")
    
    #OTP
    data_to_send = current_datetime.strftime("OTPi"+"123456"+"D"+"%d"+"M"+"%m"+"Y"+"%Y"+"H"+"%H"+"Mi"+"%M"+"S"+"%S"+"A"+"12"+"B"+"345"+"C"+"6789"+"WA"+"134"+"WB"+"557"+"END\n") 
    date_Time_for_Json = str(t_years)+'-'+ str(t_month) + '-' + str(t_day) + ' ' + str(t_hour) + ':' + str(t_min) + ':' + str(t_sec)

    serial_port.write(data_to_send.encode()) 
    
    if not ret:
        print("เกิดข้อผิดพลาดในการอ่านเฟรมภาพ")
        subprocess.run("sudo init 6", shell=True)
        break
    
    # แสดงภาพที่ได้จากกล้อง
    cv2.imshow("Camera Steaming", frame)

    #รอรับคำสั่งจากผู้ใช้
    if cv2.waitKey(1) & 0xFF == ord('o') and not recording:
        # เริ่มบันทึกวิดีโอ
        snapshot_counter = 0
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(output_mp4AndJpg_path + f'Video_{formatted_datetime}.mp4', fourcc, frame_rate, (frame_width, frame_height))
        recording = True
        print("Start recording")
        Door_state = 1 #door open state
        lock_state = "False"
        subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_D), str(Door_state)])
        successL = "False"
        messageL = "Lock not successful"
        successUL = "True"
        messageUL = "Unlock Successful"

    elif cv2.waitKey(1) & 0xFF == ord('k') and recording:
        # หยุดบันทึกวิดีโอ
        if out is not None:
            out.release()
            recording = False
            snapshot_interval_P1 = 1 #ทุกๆ 1 วิ
            snapshot_interval_P2 = 180 #ทุกๆ 3 นาที
            last_snapshot_time = 0
            print("Stop recording")
            print("SnapShot Success")
            Door_state = 0 #door close state
            lock_state = "True"
            subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_D), str(Door_state)])
            successL = "True"
            messageL = "Lock Successful"
            successUL = "False"
            messageUL = "Unlock not successful"

    if recording == True :
        out.write(frame)
        if snapshot_counter < 20:
            current_time = time.time()  # เวลาปัจจุบัน
            if current_time - last_snapshot_time >= snapshot_interval_P1:
                snapshot_path = f"snapshot_{formatted_datetime}_{snapshot_counter+1}.jpg"
                cv2.imwrite(output_mp4AndJpg_path + snapshot_path, frame)
                snapshot_counter += 1
                last_snapshot_time = current_time  # อัปเดตเวลาของ snapshot ล่าสุด
                print(f"Saved snapshot: {snapshot_path}")
        
        elif snapshot_counter >= 20:
            current_time = time.time()  # เวลาปัจจุบัน
            if current_time - last_snapshot_time >= snapshot_interval_P2:
                snapshot_path = f"snapshot_{formatted_datetime}_{snapshot_counter+1}.jpg"
                cv2.imwrite(output_mp4AndJpg_path + snapshot_path, frame)
                snapshot_counter += 1
                last_snapshot_time = current_time  # อัปเดตเวลาของ snapshot ล่าสุด
                print(f"Saved snapshot: {snapshot_path}")

    current_time_EMER = time.time()  # เวลาปัจจุบัน
    if current_time_EMER - last_time_EMER >= time_interval_EMER:
        # สร้าง Emergency key 10 หลัก
        emergency_key = ''.join(random.choice('0123456789') for _ in range(10))
        emergency_key = str(emergency_key)
        last_time_EMER = current_time_EMER

    #BLUETOOTH
    def check_internet_connection():
        try:
            subprocess.check_output(["sudo", "ping", "-c", "1", "192.168.11.57"])
            return True
        except subprocess.CalledProcessError:
            return False

        if check_internet_connection() == True:
            # print("Internet is connected.")
            subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_TCPIP), str(1)])

        else:
            # print("Internet is not connected.")
            subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_TCPIP), str(0)])

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Disconnect Camera")
        # subprocess.run(['gpio', '-g', 'mode', str(led_gpio_pin), 'in'])
        subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_H), str(0)])
        subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_D), str(0)])
        successL = "True"
        messageL = "Lock Successful"
        successUL = "False"
        messageUL = "Unlock not successful"
        break

    #JSON_TO_MQTT
    #write_to_JSON_MQTT
    Data_for_config = {
    "site_code" : site_code,
    "count_of_slave" : str(count_of_slave),
    "count_cabinets": str(count_cabinets),
    "deviceName":deviceName,
    "ip_address" : ip_address,
    "alarm_timer" : 10
    }

    json_Data_to_WD = {
        "cabinet_serf": "",
        "cabinet_sers": "",
        "cabinet_serc": "",
        "wacthdog_serf": "",
        "wacthdog_sers": "",
        "otp_serf": "",
        "otp_sers": "",
        "t_day": "",
        "t_month": "",
        "t_years": "",
        "t_hour": "",
        "t_min": "",
        "t_sec": ""
    }

    Update_Master_Data = {
        "cabinetList": [
            {
                "isCabinetActive": "True",
                "cabinetCode": site_code + '-1'
            }
        ],
        "siteCode": site_code,
        "isSiteActive": "True"
    }

    Update_emergency_key = {
        "siteCode": site_code,
        "cabinetList": [
            {
                "emergencyKey": emergency_key,
                "isCabinetActive": "True",
                "cabinetCode": site_code + '-1',
                "deviceName": deviceName
            }
        ],
        "isSiteActive": "True"
    }

    Get_cabinet_status = {
        "cabinets": [
            {
                "site_code": site_code,
                "cabinet_code": site_code + '-1',
                "locked": lock_state,
                "is_emergency": "No",
                "last_updated": date_Time_for_Json,
                "emerg_key": "null",
                "mac_address": "",
                "device_name": deviceName
            }
        ]
    }

    Lock_cabinet = {
        "successL": "",
        "messageL": ""
    }

    Unlock_cabinet = {
        "successUL": "",
        "messageUL": ""
    }

    Device_API = {
        "successAPI": "",
        "messageAPI": ""
    }

    Device_status_report_API = {
        "site_code": "100CP",
        "devices": [
            {
                "serial": "",
                "cabinet_code": site_code + '-1',
                "device_status_id": "0",
                "device_type_id":1,
                "event_type_id": "0",
                "dt": date_Time_for_Json
            },
            {
                "serial": "",
                "cabinet_code": site_code + '-1',
                "device_status_id": "0",
                "device_type_id":2,
                "event_type_id": "0",
                "dt": date_Time_for_Json
            },
            {
                "serial": "",
                "cabinet_code": site_code + '-1',
                "device_status_id": "0",
                "device_type_id":3,
                "event_type_id": "0",
                "dt": date_Time_for_Json
            },
            {
                "serial": "",
                "cabinet_code": site_code + '-1',
                "device_status_id": "0",
                "device_type_id":4,
                "event_type_id": "0",
                "dt": date_Time_for_Json
            },
            {
                "serial": "",
                "cabinet_code": site_code + '-1',
                "device_status_id": "0",
                "device_type_id":5,
                "event_type_id": "0",
                "dt": date_Time_for_Json
            },
            {
                "serial": "",
                "cabinet_code": site_code + '-1',
                "device_status_id": "0",
                "device_type_id":6,
                "event_type_id": "0",
                "dt": date_Time_for_Json
            },
            {
                "serial": "",
                "cabinet_code": site_code + '-1',
                "device_status_id": "0",
                "device_type_id":7,
                "event_type_id": "0",
                "dt": date_Time_for_Json
            },
            {
                "serial": "",
                "cabinet_code": site_code + '-1',
                "device_status_id": "0",
                "device_type_id":8,
                "event_type_id": "0",
                "dt": date_Time_for_Json
            },
            {
                "serial": "",
                "cabinet_code": site_code + '-1',
                "device_status_id": "0",
                "device_type_id":9,
                "event_type_id": "0",
                "dt": date_Time_for_Json
            },
            {
                "serial": "",
                "cabinet_code": site_code + '-1',
                "device_status_id": "0",
                "device_type_id":10,
                "event_type_id": "0",
                "dt": date_Time_for_Json
            },

        ] 
    }

    Send_emergency_API = {
        "emerg_key": emergency_key
    }

    Device_alarm_on_off = {
            "site_code": site_code,
            "cabinet_code": site_code + '-1',
            "alarm_timer": alarm_timer  # เปลี่ยนเป็นฟังก์ชันที่รับค่า alarm timer สำหรับตู้ที่ i
    }
    # รวมข้อมูล JSON ทั้งหมดในโค้ดลงในออบเจ็กต์ JSON

    Data_Sensor = {
        "cabinetsensor": [
            {
                "site_code": site_code,
                "cabinet_code": site_code + '-1',
                "device_name": deviceName,
                "Acce_X" :accel_x_json,
                "Acce_Y" :accel_y_json,
                "Acce_Z" :accel_z_json,
                "Gyro_X" :gyro_x_json,
                "Gyro_Y" :gyro_y_json,
                "Gyro_Z" :gyro_z_json,
                "Temperature":temp_json,
                "Humidty":hum_json,
                "PIR":PIR_state
            }
        ]
    }

    #plublic_to_MQTT
    client.publish("send_TINKER/Data_for_config", json.dumps(Data_for_config))
    client.publish("send_TINKER/Update_Master_Data", json.dumps(Update_Master_Data))
    client.publish("send_TINKER/Update_emergency_key", json.dumps(Update_emergency_key))
    client.publish("send_TINKER/Get_cabinet_status", json.dumps(Get_cabinet_status))
    client.publish("send_TINKER/Device_status_report_API", json.dumps(Device_status_report_API))
    client.publish("send_TINKER/Send_emergency_API", json.dumps(Send_emergency_API))
    client.publish("send_TINKER/Device_alarm_on_off", json.dumps(Device_alarm_on_off))
    client.publish("send_TINKER/Data_Sensor", json.dumps(Data_Sensor))
    client.publish("send_TINKER/Emergency_key", json.dumps(emergency_key))
    
    # if sd_card_usage.percent >= threshold_percent:
    #     Device_status_report_API[7]["event_type_id"] = "8"
    #     try:
    #         # ลบข้อมูลภาพและวิดีโอทั้งหมดในโฟลเดอร์
    #         for root, dirs, files in os.walk(target_folder):
    #             for file in files:
    #                 file_path = os.path.join(root, file)
    #                 os.remove(file_path)
    #                 print(f"ลบไฟล์ {file_path} สำเร็จ")
    #         print("ลบข้อมูลภาพและวิดีโอทั้งหมดในโฟลเดอร์เรียบร้อยแล้ว")
    #     except Exception as e:
    #         print(f"เกิดข้อผิดพลาดในการลบข้อมูลภาพและวิดีโอ: {e}")
    

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     print("Disconnect Camera")
    #     # subprocess.run(['gpio', '-g', 'mode', str(led_gpio_pin), 'in'])
    #     subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_H), str(0)])
    #     subprocess.run(['gpio', '-g', 'write', str(led_gpio_pin_D), str(0)])
    #     break

# คืนทรัพยากร
cap.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()
