import re
import subprocess

output = subprocess.check_output("ls /dev/video*", shell=True)
output = output.decode('utf-8')
filtered_output = re.findall(r'(/dev/video[0123]|/dev/video[45678])', output)
number_of_cameras = len(filtered_output)

print(f"Number of cameras found: {number_of_cameras}")
print("Filtered cameras:")
for camera in filtered_output:
    print(camera)
    if camera == "/dev/video7":
        Point_Vport = "/dev/video6"
    else:
        Point_Vport = "/dev/video5"
    
print(f"Number of Point_Vport: {Point_Vport}")
command = f"cvlc v4l2://{Point_Vport} --sout '#transcode{{vcodec=h264,acodec=none}}:rtp{{sdp=rtsp://:8554/}}'"
subprocess.run(command, shell=True)
