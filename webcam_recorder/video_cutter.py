import cv2
import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip
import os
import time
import datetime

""""
Webcam: W = Video 1
Screen: S = Video 2

    |-----------------------| S duration
    time creation
        |-------------| W
               =
        |-------------| W
        |-------------| S

"""

class VideoEditorGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Editor de vídeo")

        # Cria os botões de seleção de arquivo
        self.video1_button = tk.Button(self.root, text="Recorded webcam video", command=self.select_video1)
        self.video1_button.pack(pady=10)

        self.video2_button = tk.Button(self.root, text="Recorded screen video", command=self.select_video2)
        self.video2_button.pack(pady=10)

        self.process_button = tk.Button(self.root, text="Get screen video with same webcam video start time and duration", command=self.process_videos)
        self.process_button.pack(pady=10)

    def select_video1(self):
        # Abre uma caixa de diálogo para selecionar o arquivo do vídeo 1
        self.video1_path = filedialog.askopenfilename(title="Selecionar vídeo 1")

    def select_video2(self):
        # Abre uma caixa de diálogo para selecionar o arquivo do vídeo 2
        self.video2_path = filedialog.askopenfilename(title="Selecionar vídeo 2")

    def process_videos(self):
        # Carrega os dois vídeos
        video1 = VideoFileClip(self.video1_path)
        video2 = VideoFileClip(self.video2_path) 

        # Extrai as propriedades dos vídeos
        cap1 = cv2.VideoCapture(self.video1_path)

        #video 1
        file_name = os.path.basename(self.video1_path)
        video1_start_recording = file_name.split("_")[1].split(".")[0]
        test_info= file_name.split("_")[0]
        date_obj = datetime.datetime.strptime(video1_start_recording, '%Y:%m:%d %H:%M:%S')
        video1_start_recording = date_obj.strftime('%Y-%m-%d %H:%M:%S')
        
        #video 2
        file_name = os.path.basename(self.video2_path)
        datetime_obj = datetime.datetime.strptime(file_name, 'Screen Recording %Y-%m-%d at %H.%M.%S.mov')
        video2_start_recording = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

        time1 = datetime.datetime.strptime(video1_start_recording, '%Y-%m-%d %H:%M:%S')
        print("time1 ", time1)

        time2 = datetime.datetime.strptime(video2_start_recording, '%Y-%m-%d %H:%M:%S')
        print("time2 ", time2)

        diff_seconds = (time1 - time2).total_seconds()
        print("diff_seconds ",diff_seconds)


        cap2 = cv2.VideoCapture(self.video2_path)
        fps2 = cap2.get(cv2.CAP_PROP_FPS)
        # Obtém a duração do vídeo mais curto
        duration = min(video1.duration, video2.duration) # = Webcam Video
        print("DURATION ", duration)
        print("diff_seconds + DURATION ", diff_seconds + duration)

     
        video2 = video2.subclip(diff_seconds, diff_seconds + duration)
        video2.write_videofile(test_info +'.mp4', fps=fps2)

        # Exibe uma mensagem de sucesso
        tk.messagebox.showinfo("Processamento concluído", "Os vídeos foram processados com sucesso!")

if __name__ == '__main__':
    root = tk.Tk()

    app = VideoEditorGUI(root)
    root.mainloop()
