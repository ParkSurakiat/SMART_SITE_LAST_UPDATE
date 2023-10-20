import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import time
import threading
import json
import serial
import datetime
import paho.mqtt.client as mqtt

# กำหนดข้อมูลสำหรับ MQTT Broker
mqtt_broker_address = 'localhost'  # แทนที่ด้วยที่อยู่ของ MQTT Broker ของคุณ

# เชื่อมต่อกับ MQTT Broker
client = mqtt.Client()
client.connect(mqtt_broker_address, 1883)

# json_connect
with open('Data_for_config.json', 'r') as openfile:
    # Reading from json file
    json_object = json.load(openfile)

write_data_mod = json_object

################
Count_from_config = write_data_mod["Data_for_config"]["count_cabinets"]
site_code = write_data_mod["Data_for_config"]["site_code"]
################
Update_Master_Data = write_data_mod["Update_Master_Data"]
################
Update_emergency_key = write_data_mod["Update_emergency_key"]
################
Get_cabinet_status = write_data_mod["Get_cabinet_status"]
################
Device_status_report_API = write_data_mod["Device_status_report_API"]
################
Send_emergency_API = write_data_mod["Send_emergency_API"]
################
Device_alarm_on_off = write_data_mod["Device_alarm_on_off"]
################
Data_Sensor = write_data_mod["Data_Sensor"]
################
print(Count_from_config)
print(site_code)

count_str_site_code = len(site_code)
count_str_site_code2 =2

print(count_str_site_code)

if int(Count_from_config)-1 >= 1:

    # modbus_connect
    logger = modbus_tk.utils.create_logger("console")

    PORT = '/dev/ttyUSB0'
    master = modbus_rtu.RtuMaster(
        serial.Serial(port=PORT, baudrate=115200, bytesize=8, parity='N', stopbits=1, xonxoff=0)
    )

    def thread_RTU():
        #Connect to the slave
        master.set_timeout(1)
        master.set_verbose(True)
        logger.info("connected")

    thr = threading.Thread(target=thread_RTU)
    thr.start()

    def func_emergency_key(client, userdata, message):
        print("sub func")
        print(message.topic, message.payload)
        
        # data = json.loads(message.payload)
        # print(data)
        print("-----------------")

    
    while True:

        # รับวันที่และเวลาปัจจุบัน
        current_datetime = datetime.datetime.now()
        # แปลงวันที่และเวลาเป็นสตริงแบบกำหนดรูปแบบ
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        t_day = current_datetime.strftime("%d")
        t_month = current_datetime.strftime("%m")
        t_years = current_datetime.strftime("%Y")
        t_hour = current_datetime.strftime("%H")
        t_min = current_datetime.strftime("%M")
        t_sec = current_datetime.strftime("%S")
        date_Time_for_Json = str(t_years)+'-'+ str(t_month) + '-' + str(t_day) + ' ' + str(t_hour) + ':' + str(t_min) + ':' + str(t_sec)

        for i in range(int(Count_from_config)-1):
            print("Read_SLAVE : ", i+1)
            try:
                # master.execute(i+1, cst.WRITE_MULTIPLE_REGISTERS, 60 , output_value=[count_str_site_code,count_str_site_code2] )
                # master.execute(i+1, cst.WRITE_SINGLE_COIL, 60, output_value=count_str_site_code)
                master.execute(i+1, modbus_tk.defines.WRITE_SINGLE_REGISTER, 170, output_value=count_str_site_code)
                amount_char = 0
                for char in site_code:
                    ascii_decimal = ord(char)
                    master.execute(i+1, modbus_tk.defines.WRITE_SINGLE_REGISTER, 171 + amount_char, output_value=ascii_decimal)
                    amount_char += 1


                read_rtu = master.execute(i+1, cst.READ_HOLDING_REGISTERS, 100, 55)
                
                #read_mod_from_slave
                Acce_X = read_rtu[0]
                Acce_Y = read_rtu[1]
                Acce_Z = read_rtu[2]
                Gyro_X = read_rtu[3]
                Gyro_Y = read_rtu[4]
                Gyro_Z = read_rtu[5]
                # tempMpu6050 = read_rtu[6]
                tempSht20 = read_rtu[7]
                humiSht20 = read_rtu[8]
                PIR = read_rtu[9]
                iscabinetActive = read_rtu[10] #1,0
                emergencyKey_A = read_rtu[11]
                emergencyKey_B = read_rtu[12]
                lockDoor = read_rtu[13] #1,0
                isEmergency = read_rtu[14] #1,0
                macAddress_1 = read_rtu[15]
                macAddress_2 = read_rtu[16]
                macAddress_3 = read_rtu[17]
                macAddress_4 = read_rtu[18]
                macAddress_5 = read_rtu[19]
                macAddress_6 = read_rtu[20]
                WacthDog_codef = read_rtu[29]
                WacthDog_codes = read_rtu[30]
                smartLock_type = read_rtu[31]
                Pinhole_Camera_type = read_rtu[32]
                IP_Camera_type = read_rtu[33]
                motionSensor_type = read_rtu[34]
                vibrationSensor_type = read_rtu[35]
                doorSwitch_type = read_rtu[36]
                SD_card_type = read_rtu[37]
                slaveController_type = read_rtu[38]
                Keyswitch_type = read_rtu[39]
                Buzzer_type = read_rtu[40]
                smartLock_status = read_rtu[41]
                Pinhole_Camera_status = read_rtu[42]
                IP_Camera_status = read_rtu[43]
                motionSensor_status = read_rtu[44]
                vibrationSensor_status = read_rtu[45]
                doorSwitch_status = read_rtu[46]
                SD_card_status = read_rtu[47]
                slaveController_status = read_rtu[48]
                Keyswitch_status = read_rtu[49]
                Buzzer_status = read_rtu[50]
                # status_bluetooth = read_rtu[41]
                #condition_mod_to_json
                if iscabinetActive == 1:
                    iscabinetActive = "True"
                else :
                    iscabinetActive = "False"
                
                if lockDoor == 1:
                    lockDoor = "True"
                else :
                    lockDoor = "False"
                
                if isEmergency == 1:
                    isEmergency = "Yes"
                else :
                    isEmergency = "No"

                macAddress_1 = hex(macAddress_1)[2:]
                macAddress_2 = hex(macAddress_2)[2:]
                macAddress_3 = hex(macAddress_3)[2:]
                macAddress_4 = hex(macAddress_4)[2:]
                macAddress_5 = hex(macAddress_5)[2:]
                macAddress_6 = hex(macAddress_6)[2:]
                
                #write_to_JSON_MQTT
                macAddress = str(macAddress_1) +':'+ str(macAddress_2)+':'+ str(macAddress_3)+':'+ str(macAddress_4)+':'+ str(macAddress_5)+':'+ str(macAddress_6)
                WacthDog_code = str(WacthDog_codef) + str(WacthDog_codes)
                emergencyKey = str(emergencyKey_A) + str(emergencyKey_B)
                Update_Master_Data["cabinetList"][i]["isCabinetActive"] = iscabinetActive
                Update_emergency_key["cabinetList"][i]["emergencyKey"] = emergencyKey
                Update_emergency_key["cabinetList"][i]["isCabinetActive"] = iscabinetActive
                Get_cabinet_status["cabinets"][i]["locked"] = lockDoor
                Get_cabinet_status["cabinets"][i]["is_emergency"] = isEmergency
                Get_cabinet_status["cabinets"][i]["emerg_key"] = emergencyKey
                Get_cabinet_status["cabinets"][i]["mac_address"] = macAddress
                # Device_status_report_API["devices"][(i*10)]["serial"] =
                Device_status_report_API["devices"][(i*10)]["device_status_id"] = smartLock_status
                Device_status_report_API["devices"][(i*10)]["event_type_id"] = smartLock_type
                Device_status_report_API["devices"][(i*10)]["dt"] = date_Time_for_Json
                Device_status_report_API["devices"][(i*10)+1]["device_status_id"] = Pinhole_Camera_status
                Device_status_report_API["devices"][(i*10)+1]["event_type_id"] = Pinhole_Camera_type
                Device_status_report_API["devices"][(i*10)+1]["dt"] = date_Time_for_Json
                Device_status_report_API["devices"][(i*10)+2]["device_status_id"] = IP_Camera_status
                Device_status_report_API["devices"][(i*10)+2]["event_type_id"] = IP_Camera_type
                Device_status_report_API["devices"][(i*10)+2]["dt"] = date_Time_for_Json
                Device_status_report_API["devices"][(i*10)+3]["device_status_id"] = motionSensor_status
                Device_status_report_API["devices"][(i*10)+3]["event_type_id"] = motionSensor_type
                Device_status_report_API["devices"][(i*10)+3]["dt"] = date_Time_for_Json
                Device_status_report_API["devices"][(i*10)+4]["device_status_id"] = vibrationSensor_status
                Device_status_report_API["devices"][(i*10)+4]["event_type_id"] = vibrationSensor_type
                Device_status_report_API["devices"][(i*10)+4]["dt"] = date_Time_for_Json
                Device_status_report_API["devices"][(i*10)+5]["device_status_id"] = doorSwitch_status
                Device_status_report_API["devices"][(i*10)+5]["event_type_id"] = doorSwitch_type
                Device_status_report_API["devices"][(i*10)+5]["dt"] = date_Time_for_Json
                Device_status_report_API["devices"][(i*10)+6]["device_status_id"] = SD_card_status
                Device_status_report_API["devices"][(i*10)+6]["event_type_id"] = SD_card_type
                Device_status_report_API["devices"][(i*10)+6]["dt"] = date_Time_for_Json
                Device_status_report_API["devices"][(i*10)+7]["device_status_id"] = slaveController_status
                Device_status_report_API["devices"][(i*10)+7]["event_type_id"] = slaveController_type
                Device_status_report_API["devices"][(i*10)+7]["dt"] = date_Time_for_Json
                Device_status_report_API["devices"][(i*10)+8]["device_status_id"] = Keyswitch_status
                Device_status_report_API["devices"][(i*10)+8]["event_type_id"] = Keyswitch_type
                Device_status_report_API["devices"][(i*10)+8]["dt"] = date_Time_for_Json
                Device_status_report_API["devices"][(i*10)+9]["device_status_id"] = Buzzer_status
                Device_status_report_API["devices"][(i*10)+9]["event_type_id"] = Buzzer_type
                Device_status_report_API["devices"][(i*10)+9]["dt"] = date_Time_for_Json

                Send_emergency_API["emerg_key"] = emergencyKey
                Device_alarm_on_off[i]["alarm_timer"] = write_data_mod["Data_for_config"]["alarm_timer"]
                Data_Sensor["cabinetsensor"][i]["Acce_X"] = Acce_X
                Data_Sensor["cabinetsensor"][i]["Acce_Y"] = Acce_Y
                Data_Sensor["cabinetsensor"][i]["Acce_Z"] = Acce_Z
                Data_Sensor["cabinetsensor"][i]["Gyro_X"] = Gyro_X
                Data_Sensor["cabinetsensor"][i]["Gyro_Y"] = Gyro_Y
                Data_Sensor["cabinetsensor"][i]["Gyro_Z"] = Gyro_Z
                Data_Sensor["cabinetsensor"][i]["Temperature"] = tempSht20
                Data_Sensor["cabinetsensor"][i]["Humidty"] = humiSht20
                Data_Sensor["cabinetsensor"][i]["PIR"] = PIR

                #plublic_to_MQTT
                client.publish("send_mod/Data_for_config", json.dumps(write_data_mod["Data_for_config"]))
                client.publish("send_mod/Update_Master_Data", json.dumps(write_data_mod["Update_Master_Data"]))
                client.publish("send_mod/Update_emergency_key", json.dumps(write_data_mod["Update_emergency_key"]))
                client.publish("send_mod/Get_cabinet_status", json.dumps(write_data_mod["Get_cabinet_status"]))
                client.publish("send_mod/Device_status_report_API", json.dumps(write_data_mod["Device_status_report_API"]))
                client.publish("send_mod/Send_emergency_API", json.dumps(write_data_mod["Send_emergency_API"]))
                client.publish("send_mod/Device_alarm_on_off", json.dumps(write_data_mod["Device_alarm_on_off"]))
                client.publish("send_mod/Data_Sensor", json.dumps(write_data_mod["Data_Sensor"]))
                # #read_MQTT
                
                # client.subscribe("send_TINKER/Emergency_key")
                # client.message_callback_add("send_TINKER/Emergency_key", func_emergency_key)

                #write_mod_from_tinker_board
                OTP_A = 123
                OTP_B = 456
                WD_code_A = 112
                WD_code_B = 223
                # status_server = read_rtu[51]
                # status_reset_board = read_rtu[52]
                # master.execute(i+1, modbus_tk.defines.WRITE_SINGLE_REGISTER, 170, output_value=count_str_site_code)
                # master.execute(i+1, modbus_tk.defines.WRITE_SINGLE_REGISTER, 170, output_value=count_str_site_code)
                master.execute(i+1, cst.WRITE_MULTIPLE_REGISTERS, 200, output_value=[int(t_day),int(t_month),int(t_years),int(t_hour),int(t_min),int(t_sec),int(OTP_A),int(OTP_B),int(WD_code_A),int(WD_code_B)])
                # # start the loop to receive messages
                # client.loop_forever()
                time.sleep(1)

            except modbus_tk.modbus.ModbusError as exc:
                logger.error("%s- Code=%d", exc, exc.get_exception_code())

            
