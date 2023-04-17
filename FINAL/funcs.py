import cv2
import numpy as np
from keras.models import model_from_json
from keras.models import load_model
import pyshine as ps
import time
import datetime
import matplotlib.pyplot as plt
import os
from django.conf import settings
from moviepy.video.io.VideoFileClip import VideoFileClip

import json
import plotly.graph_objs as go
from plotly.offline import plot
import subprocess
import ffmpeg
from io import BytesIO
from moviepy.editor import VideoFileClip
from django.core.files.uploadedfile import InMemoryUploadedFile


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
def get_emotions_dict_and_save_video(video, screen_video):
    #FER2013 emotions
    emotion_dict = {0: "Anger", 1: "Disgust", 2: "Fear", 3: "Enjoyment", 4: "Contempt", 5: "Sadness", 6: "Surprise"}
    #facial expressions video
    cap = cv2.VideoCapture(video)

    #screen video
    cap_output = cv2.VideoCapture(screen_video)

    emotion_model = load_model(os.path.dirname(__file__)+ '/x.h5')
    SIZE = 0.65
    X = 1
    time_emotions = {}

    if not cap.isOpened():
        print('Error: Failed to open video file')
    else:

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_balck = cap.get(cv2.CAP_PROP_FPS)

        print("FPSSS", fps)
        print( os.path.dirname(__file__) + '/' + os.path.basename(video))

        emotion_frequency = {0: 0, 1: 0, 2: 0, 3: 0, 4:0, 5: 0, 6: 0}
        print(type(os.path.basename(video)))

        print("EEE")
        print(os.path.basename(screen_video))
        print('screen_emotions_'+ os.path.basename(screen_video))
        out = cv2.VideoWriter('emotions_'+ os.path.basename(video), cv2.VideoWriter_fourcc(*'mp4v'), fps,  (1280, 720))
        output = cv2.VideoWriter('screen_emotions_'+ os.path.basename(screen_video), cv2.VideoWriter_fourcc(*'mp4v'), frame_balck,  (1730, 720))
        rectangle = np.full((720, 450, 3), 255, dtype=np.uint8)

        #out = cv2.VideoWriter(os.path.join(settings.MEDIA_ROOT, 'videos', video_file.name) , cv2.VideoWriter_fourcc(*'mp4v'), fps,  (1280, 720))

        while True:
            # Find haar cascade to draw bounding box around face
            ret, frame = cap.read()
            if not ret:
                break        
            frame = cv2.resize(frame, (1280, 720))

            ret2, frame_balck = cap_output.read()
            if not ret2:
                break        
            frame_balck = cv2.resize(frame_balck, (1280, 720))
            frame_balck = np.concatenate([frame_balck, rectangle], axis=1)

           
           #VIDEO TIME
            frame_no = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            frame_time = frame_no / fps
            seconds = int(frame_time)
            milliseconds = int((frame_time - seconds) * 1000)
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            video_time = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

            face_detector = cv2.CascadeClassifier(os.path.dirname(__file__)+'/haarcascade_frontalface_default.xml')

            #gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  #VGG16

            # detect faces available on camera
            num_faces = face_detector.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)
            #print(emotion_frequency)
            # take each face available on the camera and Preprocess it
            for (x, y, w, h) in num_faces:
                roi_gray_frame = gray_frame[y:y + h, x:x + w]
                cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)

                # predict the emotions
                emotion_prediction = emotion_model.predict(cropped_img)
                time_emotions[video_time] = emotion_prediction[0].tolist()
                max_emotion = max(emotion_prediction[0].tolist())
                index = emotion_prediction[0].tolist().index(max_emotion)
                value = emotion_frequency.get(index)
                emotion_frequency[index] = value + 1
                print(emotion_frequency)
                
                image =  ps.putBText(frame,"",text_offset_x=175,text_offset_y=160,vspace=140,hspace=170, font_scale=2.0,background_RGB=(255,255,255),text_RGB=(255,250,250), alpha = 0.3)

                cv2.putText(frame,"Emotion", (30,50), cv2.FONT_HERSHEY_DUPLEX, SIZE, (0, 0, 0), X, cv2.LINE_AA)
                cv2.putText(frame,"X", (180,50), cv2.FONT_HERSHEY_DUPLEX, SIZE, (0, 0, 0), X, cv2.LINE_AA)
                cv2.putText(frame,"Y", (280,50), cv2.FONT_HERSHEY_DUPLEX, SIZE, (0, 0, 0), X, cv2.LINE_AA)
                cv2.putText(frame,"X: Freq. ATM (%)", (30,300), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 0, 0), X, cv2.LINE_AA)
                cv2.putText(frame,"Y: Most frequent (%)", (30,325), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 0, 0), X, cv2.LINE_AA)

                max_value = max(emotion_prediction[0].tolist())
                index = emotion_prediction[0].tolist().index(max_value)
                
                if index == 0:
                    cv2.putText(frame,">", (10,80), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 1:
                    cv2.putText(frame,">", (10,110), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 2:
                    cv2.putText(frame,">", (10,140), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 3:
                    cv2.putText(frame,">", (10,170), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 4:
                    cv2.putText(frame,">", (10,200), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 5:
                    cv2.putText(frame,">", (10,230), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 6:
                    cv2.putText(frame,">", (10,260), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)

                anger = emotion_dict[0]
                cv2.putText(frame,anger, (30,80), cv2.FONT_HERSHEY_DUPLEX, SIZE, (61,61,161,255), X, cv2.LINE_AA)
                cv2.putText(frame,str("{:.2f}".format(emotion_prediction[0][0]*100)), (180,80), cv2.FONT_HERSHEY_DUPLEX, SIZE, (61,61,161,255), X, cv2.LINE_AA)
                cv2.putText(frame,str("{:.2f}".format((emotion_frequency[0]*100) / sum(emotion_frequency.values()))), (280,80), cv2.FONT_HERSHEY_DUPLEX, SIZE, (61,61,161,255), X, cv2.LINE_AA)


                disgust = emotion_dict[1]
                cv2.putText(frame,disgust, (30,110), cv2.FONT_HERSHEY_DUPLEX, SIZE, (65,153,100,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format(emotion_prediction[0][1]*100)), (180,110), cv2.FONT_HERSHEY_DUPLEX, SIZE, (65,153,100,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format((emotion_frequency[1]*100) / sum(emotion_frequency.values()))), (280,110), cv2.FONT_HERSHEY_DUPLEX, SIZE, (65,153,100,255), X, cv2.LINE_AA)

                fear = emotion_dict[2]
                cv2.putText(frame,fear, (30,140), cv2.FONT_HERSHEY_DUPLEX,SIZE, (134,57,91,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format(emotion_prediction[0][2]*100)), (180,140), cv2.FONT_HERSHEY_DUPLEX, SIZE, (134,57,91,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format((emotion_frequency[2]*100) / sum(emotion_frequency.values()))), (280,140), cv2.FONT_HERSHEY_DUPLEX, SIZE, (134,57,91,255), X, cv2.LINE_AA)

                happy = emotion_dict[3]
                cv2.putText(frame,happy, (30,170), cv2.FONT_HERSHEY_DUPLEX, SIZE, (71,99,255,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format(emotion_prediction[0][3]*100)), (180,170), cv2.FONT_HERSHEY_DUPLEX, SIZE, (71,99,255,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format((emotion_frequency[3]*100) / sum(emotion_frequency.values()))), (280,170), cv2.FONT_HERSHEY_DUPLEX, SIZE, (71,99,255,255), X, cv2.LINE_AA)

                contempt = emotion_dict[4]
                cv2.putText(frame,contempt, (30,200), cv2.FONT_HERSHEY_DUPLEX, SIZE, (81,107,183,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format(emotion_prediction[0][4]*100)), (180,200), cv2.FONT_HERSHEY_DUPLEX, SIZE, (81,107,183,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format((emotion_frequency[4]*100) / sum(emotion_frequency.values()))), (280,200), cv2.FONT_HERSHEY_DUPLEX, SIZE, (81,107,183,255), X, cv2.LINE_AA)

                sad = emotion_dict[5]
                cv2.putText(frame, sad, (30,230), cv2.FONT_HERSHEY_DUPLEX, SIZE, (174,106,63,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format(emotion_prediction[0][5]*100)), (180,230), cv2.FONT_HERSHEY_DUPLEX, SIZE, (174,106,63,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format((emotion_frequency[5]*100) / sum(emotion_frequency.values()))), (280,230), cv2.FONT_HERSHEY_DUPLEX, SIZE, (174,106,63,255), X, cv2.LINE_AA)


                surprise = emotion_dict[6]
                cv2.putText(frame, surprise, (30,260), cv2.FONT_HERSHEY_DUPLEX, SIZE, (175,175,61,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format(emotion_prediction[0][6]*100)), (180,260), cv2.FONT_HERSHEY_DUPLEX, SIZE, (175,175,61,255), X, cv2.LINE_AA)
                cv2.putText(frame, str("{:.2f}".format((emotion_frequency[6]*100) / sum(emotion_frequency.values()))), (280,260), cv2.FONT_HERSHEY_DUPLEX, SIZE, (175,175,61,255), X, cv2.LINE_AA)

                #SCREN ---------------------------------
                if index == 0:
                    cv2.putText(frame_balck,">", (1310,80), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 1:
                    cv2.putText(frame_balck,">", (1310,110), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 2:
                    cv2.putText(frame_balck,">", (1310,140), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 3:
                    cv2.putText(frame_balck,">", (1310,170), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 4:
                    cv2.putText(frame_balck,">", (1310,200), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 5:
                    cv2.putText(frame_balck,">", (1310,230), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                elif index == 6:
                    cv2.putText(frame_balck,">", (1310,260), cv2.FONT_HERSHEY_DUPLEX, SIZE, (34,139,34,0), 2, cv2.LINE_AA)
                
                cv2.putText(frame_balck,"Emotion", (1330,50), cv2.FONT_HERSHEY_DUPLEX, SIZE, (0, 0, 0), X, cv2.LINE_AA)
                cv2.putText(frame_balck,"X", (1480,50), cv2.FONT_HERSHEY_DUPLEX, SIZE, (0, 0, 0), X, cv2.LINE_AA)
                cv2.putText(frame_balck,"Y", (1580,50), cv2.FONT_HERSHEY_DUPLEX, SIZE, (0, 0, 0), X, cv2.LINE_AA)
                cv2.putText(frame_balck,"X: Freq. ATM (%)", (1330,300), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 0, 0), X, cv2.LINE_AA)
                cv2.putText(frame_balck,"Y: Most frequent (%)", (1330,325), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 0, 0), X, cv2.LINE_AA)

                anger = emotion_dict[0]
                cv2.putText(frame_balck,anger, (1330,80), cv2.FONT_HERSHEY_DUPLEX, SIZE, (61,61,161,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck,str("{:.2f}".format(emotion_prediction[0][0]*100)), (1480,80), cv2.FONT_HERSHEY_DUPLEX, SIZE, (61,61,161,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck,str("{:.2f}".format((emotion_frequency[0]*100) / sum(emotion_frequency.values()))), (1580,80), cv2.FONT_HERSHEY_DUPLEX, SIZE, (61,61,161,255), X, cv2.LINE_AA)

                disgust = emotion_dict[1]
                cv2.putText(frame_balck,disgust, (1330,110), cv2.FONT_HERSHEY_DUPLEX, SIZE, (65,153,100,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format(emotion_prediction[0][1]*100)), (1480,110), cv2.FONT_HERSHEY_DUPLEX, SIZE, (65,153,100,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format((emotion_frequency[1]*100) / sum(emotion_frequency.values()))), (1580,110), cv2.FONT_HERSHEY_DUPLEX, SIZE, (65,153,100,255), X, cv2.LINE_AA)

                fear = emotion_dict[2]
                cv2.putText(frame_balck,fear, (1330,140), cv2.FONT_HERSHEY_DUPLEX,SIZE, (134,57,91,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format(emotion_prediction[0][2]*100)), (1480,140), cv2.FONT_HERSHEY_DUPLEX, SIZE, (134,57,91,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format((emotion_frequency[2]*100) / sum(emotion_frequency.values()))), (1580,140), cv2.FONT_HERSHEY_DUPLEX, SIZE, (134,57,91,255), X, cv2.LINE_AA)

                happy = emotion_dict[3]
                cv2.putText(frame_balck,happy, (1330,170), cv2.FONT_HERSHEY_DUPLEX, SIZE, (71,99,255,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format(emotion_prediction[0][3]*100)), (1480,170), cv2.FONT_HERSHEY_DUPLEX, SIZE, (71,99,255,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format((emotion_frequency[3]*100) / sum(emotion_frequency.values()))), (1580,170), cv2.FONT_HERSHEY_DUPLEX, SIZE, (71,99,255,255), X, cv2.LINE_AA)

                contempt = emotion_dict[4]
                cv2.putText(frame_balck,contempt, (1330,200), cv2.FONT_HERSHEY_DUPLEX, SIZE, (81,107,183,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format(emotion_prediction[0][4]*100)), (1480,200), cv2.FONT_HERSHEY_DUPLEX, SIZE, (81,107,183,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format((emotion_frequency[4]*100) / sum(emotion_frequency.values()))), (1580,200), cv2.FONT_HERSHEY_DUPLEX, SIZE, (81,107,183,255), X, cv2.LINE_AA)

                sad = emotion_dict[5]
                cv2.putText(frame_balck, sad, (1330,230), cv2.FONT_HERSHEY_DUPLEX, SIZE, (174,106,63,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format(emotion_prediction[0][5]*100)), (1480,230), cv2.FONT_HERSHEY_DUPLEX, SIZE, (174,106,63,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format((emotion_frequency[5]*100) / sum(emotion_frequency.values()))), (1580,230), cv2.FONT_HERSHEY_DUPLEX, SIZE, (174,106,63,255), X, cv2.LINE_AA)


                surprise = emotion_dict[6]
                cv2.putText(frame_balck, surprise, (1330,260), cv2.FONT_HERSHEY_DUPLEX, SIZE, (175,175,61,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format(emotion_prediction[0][6]*100)), (1480,260), cv2.FONT_HERSHEY_DUPLEX, SIZE, (175,175,61,255), X, cv2.LINE_AA)
                cv2.putText(frame_balck, str("{:.2f}".format((emotion_frequency[6]*100) / sum(emotion_frequency.values()))), (1580,260), cv2.FONT_HERSHEY_DUPLEX, SIZE, (175,175,61,255), X, cv2.LINE_AA)
                
                #SCREN end ---------------------------------
                

                maxindex = int(np.argmax(emotion_prediction))
                if maxindex == 0:
                    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (61,61,161,255), 4)
                elif maxindex == 1:
                    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (65,153,100,255), 4)
                elif maxindex == 2:
                    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10),(134,57,91,255), 4)
                elif maxindex == 3:
                    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (71,99,255,255), 4)
                elif maxindex == 4:
                    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (81,107,183,255), 4)
                elif maxindex == 5:
                    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (63,106,174,255), 4)
                elif maxindex == 6:
                    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (175,175,61,255), 4)
                #elif maxindex == 7:
                #    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (73, 82, 82), 4)

                cv2.putText(frame, emotion_dict[maxindex], (x+5, y-20), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            out.write(frame)
            output.write(frame_balck)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        out.release()
        cap_output.release()
        output.release()    

        cv2.destroyAllWindows()
        return out, time_emotions


#times in seconds
def split_video_range_time(video_path, start_time, end_time, output_name):
    video = VideoFileClip(video_path)
    subclip = video.subclip(start_time, end_time)
    subclip.write_videofile(output_name)


def emotion_dict_to_plot(emotion_dict):
    dict_emotions = json.loads(emotion_dict)
    anger = []
    disgust = []
    fear= []
    enjoyment= []
    contempt = []
    sadness = []
    surprise= []
    timeEmotions = []
    for time, emotions in dict_emotions.items():
        
        timeEmotions.append(time)
        anger.append(emotions[0])
        disgust.append(emotions[1])
        fear.append(emotions[2])
        enjoyment.append(emotions[3])
        contempt.append(emotions[4])
        sadness.append(emotions[5])
        surprise.append(emotions[6])
    
        #print(len(timeEmotions))
    x_data = [datetime.datetime.strptime(x, '%M:%S:%f').strftime('%M:%S') for x in timeEmotions]
    
    #RGB
    #BGR
    # Define your traces
    trace1 = go.Scatter(x=x_data, y=anger, name='Anger')
    trace1.line.color = 'rgb(161,61,61)' 
    
    trace2 = go.Scatter(x=x_data, y=disgust, name='Disgust')
    trace2.line.color = 'rgb(100,153,65)' 

    trace3 = go.Scatter(x=x_data, y=fear, name='Fear')
    trace3.line.color = 'rgb(91,57,134)' 

    trace4 = go.Scatter(x=x_data, y=enjoyment, name='Enjoyment')
    trace4.line.color = 'rgb(255,99,71)' 

    trace5 = go.Scatter(x=x_data, y=contempt, name='Contempt')
    trace5.line.color = 'rgb(183,107,81)' 

    trace6 = go.Scatter(x=x_data, y=sadness, name='Sadness')
    trace6.line.color = 'rgb(63,106,174)' 

    trace7 = go.Scatter(x=x_data, y=surprise, name='Surprise')
    trace7.line.color = 'rgb(61,175,175)' 

    # Define your layout
    layout = go.Layout(
        title={
        'text': 'Relative frequency of facial emotions over time',
        'x': 0.5, # Center the title
        'y': 0.85, # set y position closer to plot

        'xanchor': 'center' # Center the title horizontally
    },    

        xaxis=dict(title='Time (M:S)',  tickmode='linear', tickformat='%M'),
        yaxis=dict(title='Probability of Emotions (%)'),
        font=dict( size=11),
        
    
        )

    # Define your figure and add traces and layout
    fig = go.Figure(data=[trace1, trace2,trace3, trace4,trace5, trace6,trace7], layout=layout)
    fig.update

    fig.update_yaxes(autotypenumbers="convert types")
    # Generate an HTML representation of the plot
    plot_div = plot(fig, output_type='div', include_plotlyjs=True)


    return plot_div

def filter_dict_by_time(original_dict, start_time, end_time):
    new_dict = {}
    for key in original_dict:
        minute, second, millisec = str(key).split(':')
        total_millisec = int(minute) * 60 * 1000 + int(second) * 1000 + int(millisec)
        if total_millisec >= start_time  and total_millisec <= end_time :
            new_dict[key] = original_dict[key]
    return new_dict

def convert_to_mp4(input_file_path, output_file_path):
    input_stream = ffmpeg.input(input_file_path)
    output_stream = ffmpeg.output(input_stream, input_file_path[:-4] + "_conv.mp4", vcodec="libx264", acodec="aac")
    ffmpeg.run(output_stream)

def file_to_memory(file_path):
    with open(file_path, 'rb') as f:
        file_data = BytesIO(f.read())
    return InMemoryUploadedFile(file_data, 'file', file_path, 'video/mp4', len(file_data.getvalue()), None)