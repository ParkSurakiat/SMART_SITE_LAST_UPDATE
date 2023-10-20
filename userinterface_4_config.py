import tkinter as tk
import json

def save_data():
    site_code = site_code_entry.get()
    count_of_cabinet = count_of_cabinet_entry.get()
    ip_address = ip_address_entry.get()
    alarm_timer = alarm_timer_entry.get()

    print(site_code)
    print(count_of_cabinet)
    print(ip_address)
    print(alarm_timer)
    # siteCode = site_code
    # count_of_Cabinet = count_of_cabinet
    # IP_address = ip_address
    # Alarm_timer = alarm_timer
    # # เขียนข้อมูลลงในไฟล์ Python
    # with open("data.txt", "w") as file:
    #     file.write(f"Site Code: {site_code}\n")
    #     file.write(f"Count of Cabinet: {count_of_cabinet}\n")
    #     file.write(f"IP Address: {ip_address}\n")

    Data_from_userinterface = {
        "site_code" : site_code,
        "count_cabinets": str(count_of_cabinet),
        "ip_address" : ip_address,
        "alarm_timer" : alarm_timer
    }
    with open('/home/linaro/AIS_PARK_NEW/Data_from_userinterface.json', 'w') as json_file:
        json.dump(Data_from_userinterface, json_file, indent=4)
    
    # ล้างข้อมูลในช่องกรอก
    site_code_entry.delete(0, tk.END)
    count_of_cabinet_entry.delete(0, tk.END)
    ip_address_entry.delete(0, tk.END)
    alarm_timer_entry.delete(0, tk.END)
    


# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("กรอกข้อมูล")

# สร้างแท็บและเฟรม
frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

# สร้างตัวแปรและตัวอินพุตข้อมูล
site_code_label = tk.Label(frame, text="Site Code:")
site_code_label.pack()
site_code_entry = tk.Entry(frame)
site_code_entry.pack()

count_of_cabinet_label = tk.Label(frame, text="Count of Cabinet:")
count_of_cabinet_label.pack()
count_of_cabinet_entry = tk.Entry(frame)
count_of_cabinet_entry.pack()

ip_address_label = tk.Label(frame, text="IP Address:")
ip_address_label.pack()
ip_address_entry = tk.Entry(frame)
ip_address_entry.pack()

alarm_timer_label = tk.Label(frame, text="alarm timer:")
alarm_timer_label.pack()
alarm_timer_entry = tk.Entry(frame)
alarm_timer_entry.pack()

siteCode = ""
count_of_Cabinet = ""
IP_address = ""
Alarm_timer = ""
# สร้างปุ่มบันทึกข้อมูล
save_button = tk.Button(frame, text="บันทึกข้อมูล", command=save_data)
save_button.pack()

##############
# site_code, count_of_cabinet, ip_address, alarm_timer = save_data()
# print(site_code)
# print(count_of_cabinet)
# print(ip_address)
# print(alarm_timer)

# เริ่มการทำงานของโปรแกรม
root.mainloop()
