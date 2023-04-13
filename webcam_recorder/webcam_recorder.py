
import cv2
import tkinter as tk

from tkinter import *
import threading
import datetime
import os



video = cv2.VideoCapture(0)

frame_width = int(video.get(3))
frame_height = int(video.get(4))
   
WEBCAM_SIZE = (frame_width, frame_height)
print(WEBCAM_SIZE)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
webcam_output_video = None

window = tk.Tk()
window.title("Webcam Recorder")
window.geometry("295x140")


Filename_monitor = StringVar()
entry = Entry(window, textvariable=Filename_monitor, width=39, font="arial 12 ")
entry.place(x=5, y = 5)
entry.insert(0, "Sample name")


userType = StringVar()
entry1 = Entry(window, textvariable=userType, width=39, font="arial 12  ")
entry1.place(x=5, y = 35)
entry1.insert(0, "User type")

local = StringVar()
entry2 = Entry(window, textvariable=local, width=39, font="arial 12 ")
entry2.place(x=5, y = 65)
entry2.insert(0, "Local")

def start_recording():
    print("AAA" ,entry.get())


    
    global webcam_output_video
    #webcam_file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 video files", "*.mp4")])
    date = datetime.datetime.now()
    date_info="_" + str(date.year) +":"+ str(date.month) +":"+ str(date.day) + " " + str(date.hour) +":"+str(date.minute) +":"+str(date.second) +".mp4" 
    
    webcam_name = entry.get() + "+"+entry1.get() +"+"+ entry2.get() + date_info


    webcam_output_video = cv2.VideoWriter(webcam_name, fourcc, 30, WEBCAM_SIZE)
    print("DD ",webcam_output_video )

    webcam_thread = threading.Thread(target=record_webcam)
    webcam_thread.start()

def stop_recording():
    global stop
    stop = True

def record_webcam():
    global webcam_output_video
    # Open webcam capture object
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_SIZE[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_SIZE[1])
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        webcam_output_video.write(frame)
        if stop:
            break
    cap.release()
    webcam_output_video.release()
    os._exit(1)

    
start_button = tk.Button(window, text="Start Recording", command=start_recording)
start_button.pack(pady=10)
start_button.place(x=10, y = 110)

stop_button = tk.Button(window, text="Stop Recording", command=stop_recording)
stop_button.pack(pady=10)
stop_button.place(x=160, y = 110)


stop = False
window.mainloop()

