import os
i=0
while True:
    if(i<100):
        os.system("ssh -fN -R 33333:localhost:8080 sice@10.33.32.9 && /usr/local/bin/mjpg_streamer -i \"/usr/local/lib/mjpg-streamer/input_uvc.so -n -f 30 -r 1280x720\" -o \"/usr/local/lib/mjpg-streamer/output_http.so -p 8080 -w /usr/local/share/mjpg-streamer/www"")
        i=i+1
    else:
        break