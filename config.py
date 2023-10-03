import json
# ตั้งค่าข้อมูลต่าง ๆ และสร้าง JSON ของแต่ละประเภทข้อมูล
# (ให้ใส่ข้อมูลที่ไม่มีการกำหนดไว้ในโค้ดในส่วนนี้)

# กำหนดข้อมูลที่ใช้ในลูป
site_code = "BKKTM"
count_cabinets = 2
count_of_slave = count_cabinets-1
deviceName = 'SmartSite_' + site_code
ip_address = '192.168.11.104'
count_device = 10

# สร้างรหัสตู้ cabinet และเก็บในอาร์เรย์ cabinet_code
cabinet_code = {}
for i in range(1, count_cabinets+1):
    cabinet_code[i] = site_code + '-' + str(i)
    print(i)

# # สร้างรูปแบบข้อมูล JSON สำหรับแต่ละประเภทข้อมูล
# Interrupt = {
#     "Main_out" : "",
#     "Mod_out" : ""
# }

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
            "isCabinetActive": "False",
            "cabinetCode": cabinet_code[i+1]
        }
        for i in range(1, count_cabinets)
    ],
    "siteCode": site_code,
    "isSiteActive": "True"
}

Update_emergency_key = {
    "siteCode": site_code,
    "cabinetList": [
        {
            "emergencyKey": "",
            "isCabinetActive": "False",
            "cabinetCode": cabinet_code[i+1],
            "deviceName": deviceName
        }
        for i in range(1, count_cabinets)
    ],
    "isSiteActive": "True"
}

Get_cabinet_status = {
    "cabinets": [
        {
            "site_code": site_code,
            "cabinet_code": cabinet_code[i+1],
            "locked": "",
            "is_emergency": "No",
            "last_updated": "",
            "emerg_key": "null",
            "mac_address": "",
            "device_name": deviceName
        }
        for i in range(1, count_cabinets)
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
            "cabinet_code": cabinet_code[j+1],
            "device_status_id": "0",
            "device_type_id":str(i),
            "event_type_id": "0",
            "dt": ""
        } for j in range(1, count_cabinets)
            for i in range(1, count_device + 1)
    ] 
}

Send_emergency_API = {
    "emerg_key": ""
}

Device_alarm_on_off = []

for i in range(1, count_cabinets):
    device_alarm_data = {
        "site_code": site_code,
        "cabinet_code": cabinet_code[i+1],
        "alarm_timer": ""  # เปลี่ยนเป็นฟังก์ชันที่รับค่า alarm timer สำหรับตู้ที่ i
    }
    Device_alarm_on_off.append(device_alarm_data)
# รวมข้อมูล JSON ทั้งหมดในโค้ดลงในออบเจ็กต์ JSON

Data_Sensor = {
    "cabinetsensor": [
        {
            "site_code": site_code,
            "cabinet_code": cabinet_code[i+1],
            "device_name": deviceName,
            "Acce_X" :"",
            "Acce_Y" :"",
            "Acce_Z" :"",
            "Gyro_X" :"",
            "Gyro_Y" :"",
            "Gyro_Z" :"",
            "Temperature":"",
            "Humidty":"",
            "PIR":""
        }
        for i in range(1, count_cabinets)
    ]
}

all_data = {
    "Data_for_config" : Data_for_config ,
    "json_Data_to_WD": json_Data_to_WD,
    "Update_Master_Data": Update_Master_Data,
    "Update_emergency_key": Update_emergency_key,
    "Get_cabinet_status": Get_cabinet_status,
    "Lock_cabinet": Lock_cabinet,
    "Unlock_cabinet": Unlock_cabinet,
    "Device_API": Device_API,
    "Device_status_report_API": Device_status_report_API,
    "Send_emergency_API": Send_emergency_API,
    "Device_alarm_on_off": Device_alarm_on_off,
    "Data_Sensor" : Data_Sensor
}

# ระบุชื่อของไฟล์ JSON ที่คุณต้องการเก็บข้อมูล
file_name = ["Data_for_config.json",'Count_data.json']

# บันทึกข้อมูลในไฟล์ JSON
# with open(file_name, 'w') as json_file:
#     json.dump(all_data, json_file, indent=4)

with open('Count_data.json', 'w') as json_file:
    json.dump(Data_for_config, json_file, indent=4)

with open('Data_for_config.json', 'w') as json_file:
    json.dump(all_data, json_file, indent=4)


print(f"บันทึกข้อมูลลงในไฟล์ {file_name} เรียบร้อยแล้ว")

