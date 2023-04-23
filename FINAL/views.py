from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as loginUser, logout as logoutUser
from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect
from django.conf.urls.static import static
from app.forms import *
from app.models import *
from app.filters import *
import plotly.offline as opy

from app.funcs import *
import subprocess
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
import io
import base64
from django import template
from django.core.files.uploadedfile import InMemoryUploadedFile
from moviepy.editor import VideoFileClip
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from moviepy.editor import *
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from moviepy.editor import VideoFileClip
import moviepy.editor as moviepy
import math
import subprocess
import ffmpeg
import json
import plotly.graph_objs as go
from plotly.offline import plot
from django.http import JsonResponse

from django.db.models import Q

"""
#TODO
- Add task name to table and everywhere
- Usability evaluation done? in Smells not working properly.
"""


def nav_TeamLeader_projects(request):
    projects_ = []
    try:
        teamLeader = TeamLeader.objects.filter(user=request.user).first()
        projects = Project.objects.filter(teamLeader=teamLeader)
        for project in projects:
            projects_.append(project)
            
    except TeamLeader.DoesNotExist:
        print("TeamLeader.DoesNotExist")
    projects_.sort(key=lambda x: x.name)

    return projects_

def nav_TeamMember_projects(request):
    projects_ = []
    projectsBool = False
    try:
        if TeamMember.objects.filter(user=request.user).exists():
            teamMember = TeamMember.objects.get(user=request.user)
            #project_Videos_teamMember = {}
            invitations = Invitations.objects.filter(teamMember=teamMember, accept=True)
            projetos = [invitation.project for invitation in invitations]
            projects_=projetos
            """
            for projeto in projetos:
                videos = Video.objects.filter(project=projeto)
                videos_splited = []
                for video in videos:
                    if SubVideoTask.objects.filter(video = video).exists():
                        videos_splited.append(video)
                #invitation = Invitations.objects.get(project = projeto, teamMember=teamMember)
                project_Videos_teamMember[projeto] = videos_splited
            """
            if len(projetos) != 0:
                projectsBool = True
    except TeamMember.DoesNotExist:
        print("TeamMember.DoesNotExist")
    projects_.sort(key=lambda x: x.name)

    return projectsBool, projects_


#TEAM MEMBER VIEW--------------------------------------------------------------------------------------------------------------

def invitations_notifications(request):
    notificationsBool = False
    teamMember = TeamMember.objects.filter(user=request.user).first()
    invitations = Invitations.objects.filter(teamMember=teamMember)
    for invitation in invitations:
        if invitation.accept == False:
            notificationsBool = True        
    return notificationsBool

def manage_teamMember_Invitations(request):
    if request.user.is_authenticated:
        projectBool, projects= nav_TeamMember_projects(request)
        invitations_ = []
  
        invitationsBool = False
        try:
            teamMember = TeamMember.objects.filter(user=request.user).first()

        except TeamMember.DoesNotExist:
            print("TeamLeader.DoesNotExist")

        if request.method == 'GET':
            print("IF -------------------------")
            form = InvitationTMSearchForm(request.POST)
            print(form)
            if form.is_valid():
                invitations = Invitations.objects.filter(teamMember=teamMember).filter(
                                                 Q(project__name__icontains= request.GET.get('proj_name')) if request.GET.get('proj_name') else Q() 
                                                & Q(project__teamLeader__user__first_name__icontains=request.GET.get('leader_name')) if request.GET.get('leader_name') else Q() 
                                                & Q(project__teamLeader__user__email__icontains= request.GET.get('teamLeaderEmail')) if request.GET.get('teamLeaderEmail') else Q() 
                                                & Q(project__start_date__gte= request.GET.get('start_date')) if request.GET.get('start_date') else Q() 
                                                & Q(project__end_date__lte=request.GET.get('end_date')) if request.GET.get('end_date') else Q())
                for invitation in invitations:
                    invitations_.append(invitation)
        else:
            print("ELSE -------------------------")

            invitations = Invitations.objects.filter(teamMember=teamMember)
            for invitation in invitations:
                invitations_.append(invitation)
                invitationsBool = True
            

        if len(invitations_)!=0:
            invitationsBool = True

        return render(request, 'manage_teamMember_Invitations.html', {'projectBool':projectBool,'projects_':projects,
                                                                      'invitations': set(invitations_), 
                                                                      'invitationsBool':invitationsBool, 
                                                                      'notificationsBool':invitations_notifications(request)}) 
    return redirect('login')

def accept_teamMember_Invitation(request, id):
    if request.user.is_authenticated:
        invitation = Invitations.objects.get(id=id)
        invitation.accept = True
        invitation.save()
        return HttpResponseRedirect('/manage_teamMember_Invitations/')
    return redirect('login')

#-------------------------------------------------------------------------------------------
def Smells_usability_tests_resultsConsolidation(request, id):
    if request.user.is_authenticated:
        projectBool, Allprojects= nav_TeamMember_projects(request)
        project = Project.objects.filter(id=id).first()

        videos_dict = {}
        videos_dict_bool = False
        videos = Video.objects.filter(project__id=id) 
        """
        for video in videos:
            #apenas aparece o video splited
            if SubVideoTask.objects.filter(video = video).exists():

               #numero de subvideos (tasks) referentes ao user
               subVideoTask = SubVideoTask.objects.filter(video = video)  
                #check if exists in UsabilityEval_CW_Smells_Emotion and UsabilityEval_CW_Smells_without_Emotion
               for sV in subVideoTask:
                    if not UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask = sV, teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com")).exists():
                        usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.create(subVideoTask = sV, teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com"))
                        usabilityEval_CW_Smells_Emotion.save()
                        print("NOT ------")

                    if not UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask = sV, teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com")).exists():
                        usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.create(subVideoTask = sV, teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com"))
                        usabilityEval_CW_Smells_without_Emotion.save()
                        print("NOT ------")
        """
        for video in videos:
            #apenas aparece o video splited
            if SubVideoTask.objects.filter(video = video).exists():
                subVideoTask = SubVideoTask.objects.filter(video = video)  
                #check if exists in UsabilityEval_CW_Smells_Emotion and UsabilityEval_CW_Smells_without_Emotion
                for sV in subVideoTask:
                    if not ResultsConsulidation.objects.filter(subVideoTask = sV).exists():
                        resultsConsulidation = ResultsConsulidation.objects.create(subVideoTask = sV)
                        resultsConsulidation.save()

        videos_dict = {}
        for video in videos:
            resultsConsulidatioPermission = ResultsConsulidationPermission.objects.filter(video=video).exists()
            if resultsConsulidatioPermission:
                videos_dict[video] = True
            else:
                videos_dict[video] = False

        if len(videos_dict) != 0:
            videos_dict_bool = True
        return render(request, 'Smells_usability_tests_resultsConsolidation.html', {'project_name':project.name,
                                                           'videos_dict': videos_dict,
                                                            'projectBool':projectBool,
                                                            'projects_':Allprojects,'videos_dict_bool':videos_dict_bool}) 
    return redirect('login')

def Smells_tasks_resultsConsolidation(request, x, projName, projID, id):
    #x: with/without emotions
    #id: video ID
    if request.user.is_authenticated:
        projectBool, Allprojects= nav_TeamMember_projects(request)
        teamMember = TeamMember.objects.get(user=request.user)

        subVideo_by_userUID = SubVideoTask.objects.filter(video_id=id)
        #print("subVideo_by_userUID   ", subVideo_by_userUID)
        video_dict={}
        for sV in subVideo_by_userUID:
          
            data= []
            data.append(sV.task_number) #0
            data.append(sV.video.usability_test_name)  #1
            actions_ = []
            actions = sV.actions.split("#")
            for action in actions:
                actions_.append(action)
            data.append(actions_) #2
            if x =="with_emotions":
                data.append(sV.screen_sub_video_emotions) #3

                #usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.get(subVideoTask = sV, teamMember=teamMember)
                
                #data.append(usabilityEval_CW_Smells_Emotion.usabilitySmells_done_with_emotion) #4
                resultsConsulidation = ResultsConsulidation.objects.get(subVideoTask = sV)

                data.append(resultsConsulidation.usabilitySmells_done_with_emotion) #4

            elif x =="without_emotions":
                data.append(sV.screen_sub_video_sem_emotions) #3

         
                #usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.get(subVideoTask = sV, teamMember=teamMember)
                
                #print("DD ", usabilityEval_CW_Smells_without_Emotion)
                resultsConsulidation = ResultsConsulidation.objects.get(subVideoTask = sV)

                data.append(resultsConsulidation.usabilitySmells_done_without_emotion) #4
                #data.append(usabilityEval_CW_Smells_without_Emotion.usabilitySmells_done_without_emotion) #4


            data.append(sV.id) #5
            data.append(x) #6 emotions_check
            data.append(sV.video.user_type)  #7
            data.append(sV.video.user_UID)  #8
            data.append(sV.video.local)  #9
            print("----------- ",data)
            video_dict[emotion_dict_to_plot(sV.emotions_plot_info)]=data
        return render(request,  'Smells_tasks_resultsConsolidation.html', { 'project_name':projName,
                                                    'projectID':projID, 
                                                  'emotion_type':x, 'id': id,
                                                    'video_dict':video_dict,
                                                    'projects': nav_TeamLeader_projects(request),
                                                    'projectBool':projectBool,
                                                    'projects_':Allprojects})
    else:
        return redirect('login')


def Smells_evaluateTask_resultsConsolidation(request, x, projName, projID, id):
    print("TASK ID ", id)
    emotions_check = x
    task_id = id
    subVideoTask = SubVideoTask.objects.get(id=task_id)
    print("::: ",subVideoTask.id)


    resultsConsulidation = ResultsConsulidation.objects.get(subVideoTask = subVideoTask)

    #usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.get(subVideoTask = subVideoTask,  teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com"))
    #usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.get(subVideoTask = subVideoTask, teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com"))

    projectBool, Allprojects= nav_TeamMember_projects(request)

            
    new_data = []
    if emotions_check =="with_emotions":
        data = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask = subVideoTask)  
        new_data = []
        for d in data:
            new_data.append(d.teamMember)
            new_data.append(json.loads(d.usabilitySmells_selected_with_emotion))
            new_data.append(d.usabilitySmells_notes_with_emotion)
    if emotions_check =="without_emotions":
        data = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask = subVideoTask)  
        new_data = []
        for d in data:
            new_data.append(d.teamMember)
            new_data.append(json.loads(d.usabilitySmells_selected_without_emotion))
            new_data.append(d.usabilitySmells_notes_without_emotion)



    try:
        teamLeader = Project.objects.filter(id=projID).first().teamLeader
    except TeamLeader.DoesNotExist:
        print("TeamLeader.DoesNotExist")


    usabilitySmells = UsabilitySmells.objects.filter(teamLeader=teamLeader)

    usabilitySmells_ = []
    index = 0
    for usabilitySmell in usabilitySmells:
        usabilitySmells_.append((index, usabilitySmell.usabilitySmell, usabilitySmell.description))
        index +=1

    videoID =SubVideoTask.objects.get(id=task_id).video.id

    if request.user.is_authenticated:
        
        if request.method == 'POST':

            if emotions_check =="with_emotions":
                form = TaskWithEmotionForm(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
                    if 'usabilitySmells' in request.POST:
                        usabilitySmells = request.POST.getlist('usabilitySmells', [])
                        #options selected inside list
                        choices_selected = []
                        for uS in usabilitySmells:
                            choices_selected.append(eval(uS)[1])
                        resultsConsulidation.usabilitySmells_selected_with_emotion = json.dumps(choices_selected)

                    if data['usabilitySmells_notes_with_emotion'] != "":   
                        resultsConsulidation.usabilitySmells_notes_with_emotion = data['usabilitySmells_notes_with_emotion']
                    
                    if data['number_usability_problems_Smells_with_emotion'] != "":   
                        resultsConsulidation.number_usability_problems_Smells_with_emotion = data['number_usability_problems_Smells_with_emotion']

                    if request.POST.get('usabilitySmells_done_with_emotion', False):
                        print("XXX TRUE")

                        resultsConsulidation.usabilitySmells_done_with_emotion = True
                    else:
                        print("XXX FALSE")
                        resultsConsulidation.usabilitySmells_done_with_emotion = False
                    resultsConsulidation.save()
                    print("&&& & ", resultsConsulidation.usabilitySmells_done_with_emotion)

                    return HttpResponseRedirect('/Smells_tasks_resultsConsolidation/with_emotions/'+ str(projName) + "/"+ str(projID) + "/"+ str(videoID))

            elif emotions_check =="without_emotions":
                form = TaskWithoutEmotionForm(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
                    print(" --- ", data)
                    if 'usabilitySmells' in request.POST:
                        usabilitySmells = request.POST.getlist('usabilitySmells', [])
                        #options selected inside list
                        choices_selected = []
                        for uS in usabilitySmells:
                            choices_selected.append(eval(uS)[1])
                        resultsConsulidation.usabilitySmells_selected_without_emotion = json.dumps(choices_selected)


                    if request.POST.get('usabilitySmells_done_without_emotion', False):
                        print("TRUE")
                        resultsConsulidation.usabilitySmells_done_without_emotion = True
                    else:
                        resultsConsulidation.usabilitySmells_done_without_emotion = False

                    if data['number_usability_problems_Smells_without_emotion'] != "":   
                        resultsConsulidation.number_usability_problems_Smells_without_emotion = data['number_usability_problems_Smells_without_emotion']

                    if data['usabilitySmells_notes_without_emotion'] != "":   
                        resultsConsulidation.usabilitySmells_notes_without_emotion = data['usabilitySmells_notes_without_emotion']
   
                    resultsConsulidation.save()
                    return HttpResponseRedirect('/Smells_tasks_resultsConsolidation/without_emotions/'+ str(projName) + "/"+ str(projID) + "/"+ str(videoID))
        else:
            if emotions_check =="with_emotions":
                form = TaskWithEmotionForm(initial={
          
                    'usabilitySmells_notes_with_emotion': resultsConsulidation.usabilitySmells_notes_with_emotion,
                    'usabilitySmells_done_with_emotion': resultsConsulidation.usabilitySmells_done_with_emotion,
                    'number_usability_problems_Smells_with_emotion': resultsConsulidation.number_usability_problems_Smells_with_emotion,

                })
            elif emotions_check =="without_emotions":
                form = TaskWithoutEmotionForm(initial={
        
                    'usabilitySmells_notes_without_emotion': resultsConsulidation.usabilitySmells_notes_without_emotion,
                    'usabilitySmells_done_without_emotion': resultsConsulidation.usabilitySmells_done_without_emotion,
                    'number_usability_problems_Smells_without_emotion': resultsConsulidation.number_usability_problems_Smells_without_emotion,

                })

        return render(request, 'Smells_evaluateTask_resultsConsolidation.html', {'videoID':videoID,'emotions_check':emotions_check, 'task_id':task_id, 
                                                            'screen_sub_video_sem_emotions':subVideoTask.screen_sub_video_sem_emotions,
                                                            'screen_sub_video_emotions':subVideoTask.screen_sub_video_emotions,
                                                             'task_number':subVideoTask.task_number,'usabilitySmells':usabilitySmells_,
                                                             'emotions_plot_info':emotion_dict_to_plot(subVideoTask.emotions_plot_info), 
                                                             'form': form, 'uS_with_emotions': json.loads(resultsConsulidation.usabilitySmells_selected_with_emotion),
                                                             'uS_without_emotions': json.loads(resultsConsulidation.usabilitySmells_selected_without_emotion)  ,
                                                             'projects': nav_TeamLeader_projects(request),
                                                             'projectBool':projectBool,
                                                             'projects_':Allprojects,
                                                             'project_name':projName,
                                                             'data':new_data,
                                                             'projectID':projID})
    return redirect('login')

#-------------------------------------------------------------------------------------------
def CW_usability_tests_resultsConsolidation(request, id):
    #id = project ID
    print("PROJECT ID  ", id)
    if request.user.is_authenticated:
        projectBool, Allprojects= nav_TeamMember_projects(request)

        print("PROJECTS  ",Allprojects)

        videos_dict_bool = False
      
        videos = Video.objects.filter(project__id=id) 
        project = Project.objects.filter(id=id).first()
        print(project)
        print(videos)
        projetos = Allprojects
        videos = Video.objects.filter(project__id=id) 
        project = Project.objects.filter(id=id).first()
        print(project)
        print(videos)

        """
        for video in videos:
            #apenas aparece o video splited
            if SubVideoTask.objects.filter(video = video).exists():
               teamMember = TeamMember.objects.get(user=request.user)

               #numero de subvideos (tasks) referentes ao user
               subVideoTask = SubVideoTask.objects.filter(video = video)  
                #check if exists in UsabilityEval_CW_Smells_Emotion and UsabilityEval_CW_Smells_without_Emotion
               for sV in subVideoTask:
                    if not UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask = sV, teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com")).exists():
                        usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.create(subVideoTask = sV,teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com"))
                        usabilityEval_CW_Smells_Emotion.save()

                    if not UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask = sV, teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com")).exists():
                        usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.create(subVideoTask = sV, teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com"))
                        usabilityEval_CW_Smells_without_Emotion.save()
        """
        for video in videos:
            #apenas aparece o video splited
            if SubVideoTask.objects.filter(video = video).exists():
                subVideoTask = SubVideoTask.objects.filter(video = video)  
                #check if exists in UsabilityEval_CW_Smells_Emotion and UsabilityEval_CW_Smells_without_Emotion
                for sV in subVideoTask:
                    if not ResultsConsulidation.objects.filter(subVideoTask = sV).exists():
                        resultsConsulidation = ResultsConsulidation.objects.create(subVideoTask = sV)
                        resultsConsulidation.save()


        videos_dict = {}
        for video in videos:
            resultsConsulidatioPermission = ResultsConsulidationPermission.objects.filter(video=video).exists()
            if resultsConsulidatioPermission:
                videos_dict[video] = True
            else:
                videos_dict[video] = False

       
        if len(videos) != 0:
            videos_dict_bool = True
        return render(request, 'CW_usability_tests_resultsConsolidation.html', {'project_name':project.name,
                                                           'videos_dict': videos_dict,
                                                            'projectBool':projectBool,
                                                            'projects_':Allprojects,
                                                            'videos_dict_bool':videos_dict_bool}) 
    return redirect('login')

def CW_tasks_resultsConsolidation(request, x, projName, projID, id):
    #x: with/without emotions
    #id: video ID
    if request.user.is_authenticated:
        projectBool, Allprojects= nav_TeamMember_projects(request)

        subVideo_by_userUID = SubVideoTask.objects.filter(video_id=id)
        teamMember = TeamMember.objects.get(user=request.user)

        video_dict={}
        for sV in subVideo_by_userUID:
            data= []
            data.append(sV.task_number) #0
            data.append(sV.created_at)  #1
            actions_ = []
            actions = sV.actions.split("#")
            for action in actions:
                actions_.append(action)
            data.append(actions_) #2
            if x =="with_emotions":
                data.append(sV.screen_sub_video_emotions) #3
                #usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.get(subVideoTask = sV, teamMember=teamMember)
                resultsConsulidation = ResultsConsulidation.objects.get(subVideoTask = sV)

                data.append(resultsConsulidation.eval_done_with_emotion) #4

            elif x =="without_emotions":
                data.append(sV.screen_sub_video_sem_emotions) #3
                usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.get(subVideoTask = sV,teamMember=teamMember)
                print("DD ", usabilityEval_CW_Smells_without_Emotion.eval_done_without_emotion)

                resultsConsulidation = ResultsConsulidation.objects.get(subVideoTask = sV)

                data.append(resultsConsulidation.eval_done_without_emotion) #4
                #data.append(usabilityEval_CW_Smells_without_Emotion.eval_done_without_emotion) #4

            data.append(sV.id) #5
            data.append(x) #6 emotions_check
            data.append(sV.video.user_type)  #7
            data.append(sV.video.user_UID)  #8
            data.append(sV.video.local)  #9

            print("DATA ---------- ", data)
            video_dict[emotion_dict_to_plot(sV.emotions_plot_info)]=data
        return render(request,  'CW_tasks_resultsConsolidation.html', {'project_name':projName,
                                                    'projectID':projID, 
                                                  'emotion_type':x, 'id': id,
                                                    'video_dict':video_dict,
                                                    'projects': nav_TeamLeader_projects(request),
                                                    'projectBool':projectBool,
                                                    'projects_':Allprojects})
    else:
        return redirect('login')
    
def CW_evaluateTask_resultsConsolidation(request, x, projName, projID, id):

    emotions_check = x
    task_id = id
    subVideoTask = SubVideoTask.objects.get(id=task_id)
    teamMember = TeamMember.objects.get(user=request.user)
    #usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.get(subVideoTask = subVideoTask, teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com"))
    #usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.get(subVideoTask = subVideoTask,teamMember=TeamMember.objects.get(user__email="x2xxx123@gmail.com"))

    resultsConsulidation = ResultsConsulidation.objects.get(subVideoTask = subVideoTask)
    print("resultsConsulidation ID --->>>> ",resultsConsulidation.id)
    videoID =SubVideoTask.objects.get(id=task_id).video.id
    actions_ = []
    actions = subVideoTask.actions.split("#")
    for action in actions:
        actions_.append(action)
    if request.user.is_authenticated:
        projectBool, Allprojects= nav_TeamMember_projects(request)
        data = []
        if emotions_check =="with_emotions":
            data = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask = subVideoTask)  
        if emotions_check =="without_emotions":
            data = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask = subVideoTask)  
        print("DTA ---", data)
    
        if request.method == 'POST':
            if emotions_check =="with_emotions":
                form = TaskWithEmotionForm(request.POST)
                print("TaskWithEmotionForm")
                if form.is_valid():
                    print("333 TaskWithEmotionForm")

                    data = form.cleaned_data
                    print("22 DATA  ", data)
                    if data['q1_with_emotion'] != "":
                        resultsConsulidation.q1_with_emotion = data['q1_with_emotion']
                    if data['q2_with_emotion'] != "":
                        resultsConsulidation.q2_with_emotion = data['q2_with_emotion']
                    if data['q3_with_emotion'] != "":
                        resultsConsulidation.q3_with_emotion = data['q3_with_emotion']
                    if data['q4_with_emotion'] != "":
                        resultsConsulidation.q4_with_emotion = data['q4_with_emotion']
                    if data['notes_with_emotion'] != "":   
                        resultsConsulidation.notes_with_emotion = data['notes_with_emotion']

                    if data['number_usability_problems_CW_with_emotion'] != "":   
                        resultsConsulidation.number_usability_problems_CW_with_emotion = data['number_usability_problems_CW_with_emotion']

                    if request.POST.get('eval_done_with_emotion', False):
                        resultsConsulidation.eval_done_with_emotion = True
                    else:
                        resultsConsulidation.eval_done_with_emotion = False
                    print("SSS  ", resultsConsulidation.eval_done_with_emotion)
                    resultsConsulidation.save()
                    return HttpResponseRedirect('/CW_tasks_resultsConsolidation/with_emotions/'+ str(projName) + "/"+ str(projID) + "/"+ str(videoID))

            elif emotions_check =="without_emotions":
                form = TaskWithoutEmotionForm(request.POST)
                print("TaskWithoutEmotionForm")
                if form.is_valid():
                    print("11 111 TaskWithoutEmotionForm")

                    data = form.cleaned_data
                    print("DATA  ", data)
                    if request.POST.get('eval_done_without_emotion', False):
                        print("TRUE ---")
                        resultsConsulidation.eval_done_without_emotion = True
                    else:
                        resultsConsulidation.eval_done_without_emotion = False

                    if data['number_usability_problems_CW_without_emotion'] != "":   
                        resultsConsulidation.number_usability_problems_CW_without_emotion = data['number_usability_problems_CW_without_emotion']

                    if data['q1_without_emotion'] != "":
                        resultsConsulidation.q1_without_emotion = data['q1_without_emotion']
                    if data['q2_without_emotion'] != "":
                        resultsConsulidation.q2_without_emotion = data['q2_without_emotion']
                    if data['q3_without_emotion'] != "":
                        resultsConsulidation.q3_without_emotion = data['q3_without_emotion']
                    if data['q4_without_emotion'] != "":
                        resultsConsulidation.q4_without_emotion = data['q4_without_emotion']
                    if data['notes_without_emotion'] != "":   
                        resultsConsulidation.notes_without_emotion = data['notes_without_emotion']
                    resultsConsulidation.save()
                    return HttpResponseRedirect('/CW_tasks_resultsConsolidation/without_emotions/'+ str(projName) + "/"+ str(projID) + "/"+ str(videoID))
        else:
            if emotions_check =="with_emotions":
                form = TaskWithEmotionForm(initial={
                    'q1_with_emotion': resultsConsulidation.q1_with_emotion,
                    'q2_with_emotion': resultsConsulidation.q2_with_emotion,
                    'q3_with_emotion': resultsConsulidation.q3_with_emotion,
                    'q4_with_emotion': resultsConsulidation.q4_with_emotion,
                    'notes_with_emotion': resultsConsulidation.notes_with_emotion,
                    'eval_done_with_emotion': resultsConsulidation.eval_done_with_emotion,
                    'number_usability_problems_CW_with_emotion': resultsConsulidation.number_usability_problems_CW_with_emotion,

                })
            elif emotions_check =="without_emotions":
                form = TaskWithoutEmotionForm(initial={
                    'q1_without_emotion': resultsConsulidation.q1_without_emotion,
                    'q2_without_emotion': resultsConsulidation.q2_without_emotion,
                    'q3_without_emotion': resultsConsulidation.q3_without_emotion,
                    'q4_without_emotion': resultsConsulidation.q4_without_emotion,
                    'notes_without_emotion': resultsConsulidation.notes_without_emotion,
                    'eval_done_without_emotion': resultsConsulidation.eval_done_without_emotion,
                    'number_usability_problems_CW_without_emotion': resultsConsulidation.number_usability_problems_CW_without_emotion,

                })

        return render(request, 'CW_evaluateTask_resultsConsolidation.html', {'project_name':projName,
                                                    'projectID':projID,
                                                    'projects': nav_TeamLeader_projects(request),'videoID':videoID,
                                                    'emotions_check':emotions_check, 'task_id':task_id, 
                                                    'screen_sub_video_sem_emotions':subVideoTask.screen_sub_video_sem_emotions,
                                                    'screen_sub_video_emotions':subVideoTask.screen_sub_video_emotions, 
                                                    'task_number':subVideoTask.task_number,'actions':actions_,
                                                    'emotions_plot_info':emotion_dict_to_plot(subVideoTask.emotions_plot_info), 
                                                    'form': form,
                                                     'projectBool':projectBool,
                                                     'data':data,
                                                    'projects_':Allprojects})
    return redirect('login')

#-------------------------------------------------------------------------------------------
#1º
def CW_usability_tests(request, id):
    #id = project ID
    print("PROJECT ID  ", id)
    if request.user.is_authenticated:
        projectBool, Allprojects= nav_TeamMember_projects(request)

        print("PROJECTS  ",Allprojects)

        videos_dict = {}
        videos_dict_bool = False
      
        projetos = Allprojects
        videos = Video.objects.filter(project__id=id) 
        project = Project.objects.filter(id=id).first()
        print(project)
        print(videos)

        
        for video in videos:
            #apenas aparece o video splited
            if SubVideoTask.objects.filter(video = video).exists():
               teamMember = TeamMember.objects.get(user=request.user)

               #numero de subvideos (tasks) referentes ao user
               subVideoTask = SubVideoTask.objects.filter(video = video)  
                #check if exists in UsabilityEval_CW_Smells_Emotion and UsabilityEval_CW_Smells_without_Emotion
               for sV in subVideoTask:
                    if not UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask = sV, teamMember=teamMember).exists():
                        usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.create(subVideoTask = sV, teamMember=teamMember)
                        usabilityEval_CW_Smells_Emotion.save()

                    if not UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask = sV, teamMember=teamMember).exists():
                        usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.create(subVideoTask = sV, teamMember=teamMember)
                        usabilityEval_CW_Smells_without_Emotion.save()

               
               totalTasks_with_emotion = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember= teamMember).count()
               totalTasks_without_emotion = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember= teamMember).count()

               #totalTasks = SubVideoTask.objects.filter(video = video).count()
               totalTasks_done_with_emotions = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,eval_done_with_emotion=True).count()
               totalTasks_done_without_emotions = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,eval_done_without_emotion=True).count()
               
               data= []
               data.append(totalTasks_done_without_emotions) #0 total tasks with emotion done
               data.append(totalTasks_without_emotion) #1 total tasks with emotion
               data.append(totalTasks_done_with_emotions) #2 total tasks without emotion done
               data.append(totalTasks_with_emotion) #4 total tasks without emotion

               videos_dict[video] = data
               if len(videos_dict) != 0:
                    videos_dict_bool = True
        return render(request, 'CW_usability_tests.html', {'project_name':project.name,
                                                           'videos_dict': videos_dict,
                                                            'projectBool':projectBool,
                                                            'projects_':Allprojects,
                                                            'videos_dict_bool':videos_dict_bool}) 
    return redirect('login')

#2º
def CW_tasks(request, x, projName, projID, id):
    #x: with/without emotions
    #id: video ID
    if request.user.is_authenticated:
        projectBool, Allprojects= nav_TeamMember_projects(request)

        subVideo_by_userUID = SubVideoTask.objects.filter(video_id=id)
        teamMember = TeamMember.objects.get(user=request.user)

        video_dict={}
        for sV in subVideo_by_userUID:
            data= []
            data.append(sV.task_number) #0
            data.append(sV.created_at)  #1
            actions_ = []
            actions = sV.actions.split("#")
            for action in actions:
                actions_.append(action)
            data.append(actions_) #2
            if x =="with_emotions":
                data.append(sV.screen_sub_video_emotions) #3
                usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.get(subVideoTask = sV, teamMember=teamMember)

                data.append(usabilityEval_CW_Smells_Emotion.eval_done_with_emotion) #4

                #data.append(sV.q1_with_emotion) #4
                #data.append(sV.q2_with_emotion) #5
                #data.append(sV.q3_with_emotion) #6
                #data.append(sV.q4_with_emotion) #7
                #data.append(sV.notes_with_emotion) #8

            elif x =="without_emotions":
                data.append(sV.screen_sub_video_sem_emotions) #3
                usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.get(subVideoTask = sV, teamMember=teamMember)
                print("DD ", usabilityEval_CW_Smells_without_Emotion.eval_done_without_emotion)
                data.append(usabilityEval_CW_Smells_without_Emotion.eval_done_without_emotion) #4

                #data.append(sV.q1_without_emotion) #4
                #data.append(sV.q2_without_emotion) #5
                #data.append(sV.q3_without_emotion) #6
                #data.append(sV.q4_without_emotion) #7
                #data.append(sV.notes_without_emotion) #8

            data.append(sV.id) #5
            data.append(x) #6 emotions_check
            data.append(sV.video.user_type)  #7
            data.append(sV.video.user_UID)  #8
            data.append(sV.video.local)  #9
            video_dict[emotion_dict_to_plot(sV.emotions_plot_info)]=data
        return render(request,  'CW_tasks.html', {'project_name':projName,
                                                    'projectID':projID, 
                                                  'emotion_type':x, 'id': id,
                                                    'video_dict':video_dict,
                                                    'projects': nav_TeamLeader_projects(request),
                                                    'projectBool':projectBool,
                                                    'projects_':Allprojects})
    else:
        return redirect('login')

#3º
def CW_evaluateTask(request, x, projName, projID, id):

    emotions_check = x
    task_id = id
    subVideoTask = SubVideoTask.objects.get(id=task_id)
    teamMember = TeamMember.objects.get(user=request.user)
    usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.get(subVideoTask = subVideoTask, teamMember=teamMember)
    usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.get(subVideoTask = subVideoTask, teamMember=teamMember)



    videoID =SubVideoTask.objects.get(id=task_id).video.id
    actions_ = []
    actions = subVideoTask.actions.split("#")
    print(subVideoTask.emotions_plot_info)
    for action in actions:
        actions_.append(action)
    if request.user.is_authenticated:
        projectBool, Allprojects= nav_TeamMember_projects(request)

        if request.method == 'POST':
            if emotions_check =="with_emotions":
                form = TaskWithEmotionForm(request.POST)
                print("TaskWithEmotionForm")
                if form.is_valid():
                    print("333 TaskWithEmotionForm")

                    data = form.cleaned_data
                    print("22 DATA  ", data)
                    if data['q1_with_emotion'] != "":
                        usabilityEval_CW_Smells_Emotion.q1_with_emotion = data['q1_with_emotion']
                    if data['q2_with_emotion'] != "":
                        usabilityEval_CW_Smells_Emotion.q2_with_emotion = data['q2_with_emotion']
                    if data['q3_with_emotion'] != "":
                        usabilityEval_CW_Smells_Emotion.q3_with_emotion = data['q3_with_emotion']
                    if data['q4_with_emotion'] != "":
                        usabilityEval_CW_Smells_Emotion.q4_with_emotion = data['q4_with_emotion']
                    if data['notes_with_emotion'] != "":   
                        usabilityEval_CW_Smells_Emotion.notes_with_emotion = data['notes_with_emotion']
                    if request.POST.get('eval_done_with_emotion', False):
                        usabilityEval_CW_Smells_Emotion.eval_done_with_emotion = True
                    else:
                        usabilityEval_CW_Smells_Emotion.eval_done_with_emotion = False
                    print("SSS  ", usabilityEval_CW_Smells_Emotion.eval_done_with_emotion)
                    usabilityEval_CW_Smells_Emotion.save()
                    return HttpResponseRedirect('/CW_tasks/with_emotions/'+ str(projName) + "/"+ str(projID) + "/"+ str(videoID))

            elif emotions_check =="without_emotions":
                form = TaskWithoutEmotionForm(request.POST)
                print("TaskWithoutEmotionForm")
                if form.is_valid():
                    print("11 111 TaskWithoutEmotionForm")

                    data = form.cleaned_data
                    print("DATA  ", data)
                    if request.POST.get('eval_done_without_emotion', False):
                        usabilityEval_CW_Smells_without_Emotion.eval_done_without_emotion = True
                    else:
                        usabilityEval_CW_Smells_without_Emotion.eval_done_without_emotion = False


                    if data['q1_without_emotion'] != "":
                        usabilityEval_CW_Smells_without_Emotion.q1_without_emotion = data['q1_without_emotion']
                    if data['q2_without_emotion'] != "":
                        usabilityEval_CW_Smells_without_Emotion.q2_without_emotion = data['q2_without_emotion']
                    if data['q3_without_emotion'] != "":
                        usabilityEval_CW_Smells_without_Emotion.q3_without_emotion = data['q3_without_emotion']
                    if data['q4_without_emotion'] != "":
                        usabilityEval_CW_Smells_without_Emotion.q4_without_emotion = data['q4_without_emotion']
                    if data['notes_without_emotion'] != "":   
                        usabilityEval_CW_Smells_without_Emotion.notes_without_emotion = data['notes_without_emotion']
   
                    usabilityEval_CW_Smells_without_Emotion.save()
                    return HttpResponseRedirect('/CW_tasks/without_emotions/'+ str(projName) + "/"+ str(projID) + "/"+ str(videoID))
        else:
            if emotions_check =="with_emotions":
                form = TaskWithEmotionForm(initial={
                    'q1_with_emotion': usabilityEval_CW_Smells_Emotion.q1_with_emotion,
                    'q2_with_emotion': usabilityEval_CW_Smells_Emotion.q2_with_emotion,
                    'q3_with_emotion': usabilityEval_CW_Smells_Emotion.q3_with_emotion,
                    'q4_with_emotion': usabilityEval_CW_Smells_Emotion.q4_with_emotion,
                    'notes_with_emotion': usabilityEval_CW_Smells_Emotion.notes_with_emotion,
                    'eval_done_with_emotion': usabilityEval_CW_Smells_Emotion.eval_done_with_emotion,

                })
            elif emotions_check =="without_emotions":
                form = TaskWithoutEmotionForm(initial={
                    'q1_without_emotion': usabilityEval_CW_Smells_without_Emotion.q1_without_emotion,
                    'q2_without_emotion': usabilityEval_CW_Smells_without_Emotion.q2_without_emotion,
                    'q3_without_emotion': usabilityEval_CW_Smells_without_Emotion.q3_without_emotion,
                    'q4_without_emotion': usabilityEval_CW_Smells_without_Emotion.q4_without_emotion,
                    'notes_without_emotion': usabilityEval_CW_Smells_without_Emotion.notes_without_emotion,
                    'eval_done_without_emotion': usabilityEval_CW_Smells_without_Emotion.eval_done_without_emotion,
                })

        return render(request, 'CW_evaluateTask.html', {'project_name':projName,
                                                    'projectID':projID,
                                                    'projects': nav_TeamLeader_projects(request),'videoID':videoID,
                                                    'emotions_check':emotions_check, 'task_id':task_id, 
                                                    'screen_sub_video_sem_emotions':subVideoTask.screen_sub_video_sem_emotions,
                                                    'screen_sub_video_emotions':subVideoTask.screen_sub_video_emotions, 
                                                    'task_number':subVideoTask.task_number,'actions':actions_,
                                                    'emotions_plot_info':emotion_dict_to_plot(subVideoTask.emotions_plot_info), 
                                                    'form': form,
                                                     'projectBool':projectBool,
                                                    'projects_':Allprojects})
    return redirect('login')

#-------------------------------------------------------------------------------------------

def Smells_usability_tests(request, id):
    if request.user.is_authenticated:
        projectBool, Allprojects= nav_TeamMember_projects(request)
        project = Project.objects.filter(id=id).first()

        videos_dict = {}
        videos_dict_bool = False
        videos = Video.objects.filter(project__id=id) 
        for video in videos:
            #apenas aparece o video splited
            if SubVideoTask.objects.filter(video = video).exists():
               teamMember = TeamMember.objects.get(user=request.user)

               #numero de subvideos (tasks) referentes ao user
               subVideoTask = SubVideoTask.objects.filter(video = video)  
                #check if exists in UsabilityEval_CW_Smells_Emotion and UsabilityEval_CW_Smells_without_Emotion
               for sV in subVideoTask:
                    if not UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask = sV, teamMember=teamMember).exists():
                        usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.create(subVideoTask = sV, teamMember=teamMember)
                        usabilityEval_CW_Smells_Emotion.save()

                    if not UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask = sV, teamMember=teamMember).exists():
                        usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.create(subVideoTask = sV, teamMember=teamMember)
                        usabilityEval_CW_Smells_without_Emotion.save()

               
               totalTasks_with_emotion = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember= teamMember).count()
               totalTasks_without_emotion = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember= teamMember).count()

               #totalTasks = SubVideoTask.objects.filter(video = video).count()
               totalTasks_done_with_emotions = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,usabilitySmells_done_with_emotion=True).count()
               totalTasks_done_without_emotions = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,usabilitySmells_done_without_emotion=True).count()
               
               data= []
               data.append(totalTasks_done_without_emotions) #0 total tasks with emotion done
               data.append(totalTasks_without_emotion) #1 total tasks with emotion
               data.append(totalTasks_done_with_emotions) #2 total tasks without emotion done
               data.append(totalTasks_with_emotion) #4 total tasks without emotion

               videos_dict[video] = data

               if len(videos_dict) !=0:
                   videos_dict_bool = True
        return render(request, 'Smells_usability_tests.html', {'project_name':project.name,
                                                           'videos_dict': videos_dict,
                                                            'projectBool':projectBool,
                                                            'projects_':Allprojects,'videos_dict_bool':videos_dict_bool}) 
    return redirect('login')

def Smells_tasks(request, x, projName, projID, id):
    #x: with/without emotions
    #id: video ID
    if request.user.is_authenticated:
        projectBool, Allprojects= nav_TeamMember_projects(request)

        subVideo_by_userUID = SubVideoTask.objects.filter(video_id=id)
        teamMember = TeamMember.objects.get(user=request.user)

        video_dict={}
        for sV in subVideo_by_userUID:
            data= []
            data.append(sV.task_number) #0
            data.append(sV.video.usability_test_name)  #1
            actions_ = []
            actions = sV.actions.split("#")
            for action in actions:
                actions_.append(action)
            data.append(actions_) #2
            if x =="with_emotions":
                data.append(sV.screen_sub_video_emotions) #3
                usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.get(subVideoTask = sV, teamMember=teamMember)

                data.append(usabilityEval_CW_Smells_Emotion.usabilitySmells_done_with_emotion) #4


            elif x =="without_emotions":
                data.append(sV.screen_sub_video_sem_emotions) #3
                usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.get(subVideoTask = sV, teamMember=teamMember)
                print("DD ", usabilityEval_CW_Smells_without_Emotion.usabilitySmells_done_without_emotion)
                data.append(usabilityEval_CW_Smells_without_Emotion.usabilitySmells_done_without_emotion) #4


            data.append(sV.id) #5
            data.append(x) #6 emotions_check
            data.append(sV.video.user_type)  #7
            data.append(sV.video.user_UID)  #8
            data.append(sV.video.local)  #9

            video_dict[emotion_dict_to_plot(sV.emotions_plot_info)]=data
        return render(request,  'Smells_tasks.html', { 'project_name':projName,
                                                    'projectID':projID, 
                                                  'emotion_type':x, 'id': id,
                                                    'video_dict':video_dict,
                                                    'projects': nav_TeamLeader_projects(request),
                                                    'projectBool':projectBool,
                                                    'projects_':Allprojects})
    else:
        return redirect('login')

def Smells_evaluateTask(request, x, projName, projID, id):
    emotions_check = x
    task_id = id
    subVideoTask = SubVideoTask.objects.get(id=task_id)
    teamMember = TeamMember.objects.get(user=request.user)
    usabilityEval_CW_Smells_Emotion = UsabilityEval_CW_Smells_Emotion.objects.get(subVideoTask = subVideoTask, teamMember=teamMember)
    usabilityEval_CW_Smells_without_Emotion = UsabilityEval_CW_Smells_without_Emotion.objects.get(subVideoTask = subVideoTask, teamMember=teamMember)

    projectBool, Allprojects= nav_TeamMember_projects(request)
    try:
        teamLeader = Project.objects.filter(id=projID).first().teamLeader
    except TeamLeader.DoesNotExist:
        print("TeamLeader.DoesNotExist")
    usabilitySmells = UsabilitySmells.objects.filter(teamLeader=teamLeader)

    usabilitySmells_ = []
    index = 0
    for usabilitySmell in usabilitySmells:
        usabilitySmells_.append((index, usabilitySmell.usabilitySmell, usabilitySmell.description))
        index +=1

    videoID =SubVideoTask.objects.get(id=task_id).video.id

    if request.user.is_authenticated:
        
        if request.method == 'POST':

            if emotions_check =="with_emotions":
                form = TaskWithEmotionForm(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
                    if 'usabilitySmells' in request.POST:
                        usabilitySmells = request.POST.getlist('usabilitySmells', [])
                        #options selected inside list
                        choices_selected = []
                        for uS in usabilitySmells:
                            choices_selected.append(eval(uS)[1])
                        usabilityEval_CW_Smells_Emotion.usabilitySmells_selected_with_emotion = json.dumps(choices_selected)

                    if data['usabilitySmells_notes_with_emotion'] != "":   
                        usabilityEval_CW_Smells_Emotion.usabilitySmells_notes_with_emotion = data['usabilitySmells_notes_with_emotion']

                    if request.POST.get('usabilitySmells_done_with_emotion', False):
                        print("XXX TRUE")

                        usabilityEval_CW_Smells_Emotion.usabilitySmells_done_with_emotion = True
                    else:
                        print("XXX FALSE")
                        usabilityEval_CW_Smells_Emotion.usabilitySmells_done_with_emotion = False
                    usabilityEval_CW_Smells_Emotion.save()
                    print("&&& & ", usabilityEval_CW_Smells_Emotion.usabilitySmells_done_with_emotion)

                    return HttpResponseRedirect('/Smells_tasks/with_emotions/'+ str(projName) + "/"+ str(projID) + "/"+ str(videoID))

            elif emotions_check =="without_emotions":
                form = TaskWithoutEmotionForm(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
                    if 'usabilitySmells' in request.POST:
                        usabilitySmells = request.POST.getlist('usabilitySmells', [])
                        #options selected inside list
                        choices_selected = []
                        for uS in usabilitySmells:
                            choices_selected.append(eval(uS)[1])
                        usabilityEval_CW_Smells_without_Emotion.usabilitySmells_selected_without_emotion = json.dumps(choices_selected)


                    if request.POST.get('usabilitySmells_done_without_emotion', False):
                        print("TRUE")
                        usabilityEval_CW_Smells_without_Emotion.usabilitySmells_done_without_emotion = True
                    else:
                        usabilityEval_CW_Smells_without_Emotion.usabilitySmells_done_without_emotion = False


                    if data['usabilitySmells_notes_without_emotion'] != "":   
                        usabilityEval_CW_Smells_without_Emotion.usabilitySmells_notes_without_emotion = data['usabilitySmells_notes_without_emotion']
   
                    usabilityEval_CW_Smells_without_Emotion.save()
                    return HttpResponseRedirect('/Smells_tasks/without_emotions/'+ str(projName) + "/"+ str(projID) + "/"+ str(videoID))
        else:
            if emotions_check =="with_emotions":
                form = TaskWithEmotionForm(initial={
          
                    'usabilitySmells_notes_with_emotion': usabilityEval_CW_Smells_Emotion.usabilitySmells_notes_with_emotion,
                    'usabilitySmells_done_with_emotion': usabilityEval_CW_Smells_Emotion.usabilitySmells_done_with_emotion,

                })
            elif emotions_check =="without_emotions":
                form = TaskWithoutEmotionForm(initial={
        
                    'usabilitySmells_notes_without_emotion': usabilityEval_CW_Smells_without_Emotion.usabilitySmells_notes_without_emotion,
                    'usabilitySmells_done_without_emotion': usabilityEval_CW_Smells_without_Emotion.usabilitySmells_done_without_emotion,
                })

        return render(request, 'Smells_evaluateTask.html', {'videoID':videoID,'emotions_check':emotions_check, 'task_id':task_id, 
                                                            'screen_sub_video_sem_emotions':subVideoTask.screen_sub_video_sem_emotions,
                                                            'screen_sub_video_emotions':subVideoTask.screen_sub_video_emotions,
                                                             'task_number':subVideoTask.task_number,'usabilitySmells':usabilitySmells_,
                                                             'emotions_plot_info':emotion_dict_to_plot(subVideoTask.emotions_plot_info), 
                                                             'form': form, 'uS_with_emotions': json.loads(usabilityEval_CW_Smells_Emotion.usabilitySmells_selected_with_emotion),
                                                             'uS_without_emotions': json.loads(usabilityEval_CW_Smells_without_Emotion.usabilitySmells_selected_without_emotion)  ,
                                                             'projects': nav_TeamLeader_projects(request),
                                                             'projectBool':projectBool,
                                                             'projects_':Allprojects,
                                                             'project_name':projName,
                                                             'projectID':projID})
    return redirect('login')


#END TEAM MEMBER VIEW--------------------------------------------------------------------------------------------------------------

#HEURISTIC EVALUATION------------------------------------------------------------------------
def manage_heuristicEvaluations(request):
    if request.user.is_authenticated:
        heuristics = []
        try:
            teamLeader = TeamLeader.objects.filter(user=request.user).first()
            heuristicEvaluations = HeuristicEvaluation.objects.filter(teamLeader=teamLeader)
            if request.method == 'GET':
                print("IT'S A GET")
                form = HeuristicEvaluationForm(request.GET)
                print(form)
                if form.is_valid():       
                    heuristicEvaluations = HeuristicEvaluation.objects.filter(Q(teamLeader=teamLeader) 
                                                          & Q(heuristicName__icontains= request.GET.get('heuristicName')) if request.GET.get('heuristicName') else Q() 
                                                        & Q(description__icontains=request.GET.get('description')) if request.GET.get('description') else Q())
                                                       
            

        except TeamLeader.DoesNotExist:
            print("TeamLeader.DoesNotExist")
        return render(request, 'manage_heuristicEvaluations.html', {  'heuristicEvaluations': heuristicEvaluations}) 

    return redirect('login')

def create_heuristicEvaluation(request):
    form = HeuristicEvaluationForm()
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = HeuristicEvaluationForm(request.POST)
            print(form)
            if form.is_valid():
                data = form.cleaned_data
                heuristicName = data['heuristicName']
                description = data['description']

                try:
                    team_leader = TeamLeader.objects.get(user=request.user)
                    heuristic = HeuristicEvaluation(teamLeader=team_leader, heuristicName=heuristicName, description=description)
                    heuristic.save()  
                except TeamLeader.DoesNotExist:
                    print("TeamLeader.DoesNotExist")

                return redirect(manage_heuristicEvaluations)
            else:
                return render(request, 'create_heuristicEvaluation.html')
        return render(request, 'create_heuristicEvaluation.html', { 'form': form, 'projects': nav_TeamLeader_projects(request)})
    return redirect('login')

def deleteHeuristicEvaluation(request, id):
    if request.user.is_authenticated:
        heuristic = HeuristicEvaluation.objects.get(id=id)
        heuristic.delete()
        return HttpResponseRedirect('/manage_heuristicEvaluations/')
    return redirect('login')

def editHeuristicEvaluation(request, id):
    try:
        teamLeader = TeamLeader.objects.filter(user=request.user).first()
        #usabilitySmells = Project.objects.filter(teamLeader=teamLeader)
    
    except TeamLeader.DoesNotExist:
        print("TeamLeader.DoesNotExist")
    if request.user.is_authenticated:
        heuristic = HeuristicEvaluation.objects.get(id=id)

        if request.method == 'POST':
            form = HeuristicEvaluationForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data['heuristicName'] != "":
                    heuristic.heuristicName = data['heuristicName']
                if data['description'] != "":
                    heuristic.description = data['description']
 
                heuristic.save()
                return redirect(manage_heuristicEvaluations) 
        else:
            form = HeuristicEvaluationForm(initial={
                'heuristicName': heuristic.heuristicName,
                'description': heuristic.description,
          
            })
        return render(request, 'editHeuristicEvaluation.html', { 'form': form,'projects': nav_TeamLeader_projects(request)})
    return redirect('login')


#-USABILITY SMELLS CRUD----------------------------------------------------------------------------------------------------
def manage_usabilitySmells(request):
    if request.user.is_authenticated:
        usabilitySmells = []
        try:
            teamLeader = TeamLeader.objects.filter(user=request.user).first()
            usabilitySmells = UsabilitySmells.objects.filter(teamLeader=teamLeader)
            if request.method == 'GET':
                print("IT'S A GET")
                form = UsabilitySmellsForm(request.GET)
                print(form)
                if form.is_valid(): 
                    data = form.cleaned_data
                    usabilitySmell = data['usabilitySmell']
                    description = data['description']
          
                    usabilitySmells = UsabilitySmells.objects.filter(Q(teamLeader=teamLeader) 
                                                          & Q(usabilitySmell__icontains= request.GET.get('usabilitySmell')) if request.GET.get('usabilitySmell') else Q() 
                                                        & Q(description__icontains=request.GET.get('description')) if request.GET.get('description') else Q())
                                                       
            

        except TeamLeader.DoesNotExist:
            print("TeamLeader.DoesNotExist")
        return render(request, 'manage_usabilitySmells.html', {  'usabilitySmells': usabilitySmells}) 

    return redirect('login')

def create_usabilitySmell(request):
    form = UsabilitySmellsForm()
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UsabilitySmellsForm(request.POST)
            print(form)
            if form.is_valid():
                data = form.cleaned_data
                usabilitySmell = data['usabilitySmell']
                description = data['description']

                try:
                    team_leader = TeamLeader.objects.get(user=request.user)
                    usabilitySmell = UsabilitySmells(teamLeader=team_leader, usabilitySmell=usabilitySmell, description=description)
                    usabilitySmell.save()  
                except TeamLeader.DoesNotExist:
                    print("TeamLeader.DoesNotExist")

                return redirect(manage_usabilitySmells)
            else:
                return render(request, 'create_usabilitySmell.html')
        return render(request, 'create_usabilitySmell.html', { 'form': form, 'projects': nav_TeamLeader_projects(request)})
    return redirect('login')

def deleteUsabilitySmell(request, id):
    if request.user.is_authenticated:
        usabilitySmell = UsabilitySmells.objects.get(id=id)
        usabilitySmell.delete()
        return HttpResponseRedirect('/manage_usabilitySmells/')
    return redirect('login')

def editUsabilitySmells(request, id):
    try:
        teamLeader = TeamLeader.objects.filter(user=request.user).first()
        #usabilitySmells = Project.objects.filter(teamLeader=teamLeader)
    
    except TeamLeader.DoesNotExist:
        print("TeamLeader.DoesNotExist")
    if request.user.is_authenticated:
        usabilitySmell = UsabilitySmells.objects.get(id=id)

        if request.method == 'POST':
            form = UsabilitySmellsForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data['usabilitySmell'] != "":
                    usabilitySmell.usabilitySmell = data['usabilitySmell']
                if data['description'] != "":
                    usabilitySmell.description = data['description']
 
                usabilitySmell.save()
                return redirect(manage_usabilitySmells) 
        else:
            form = UsabilitySmellsForm(initial={
                'usabilitySmell': usabilitySmell.usabilitySmell,
                'description': usabilitySmell.description,
          
            })
        return render(request, 'editUsabilitySmells.html', { 'form': form,'projects': nav_TeamLeader_projects(request)})
    return redirect('login')




def manage_projects(request):
    if request.user.is_authenticated:
        projects_ = []
        try:
            teamLeader = TeamLeader.objects.filter(user=request.user).first()
            projects = Project.objects.filter(teamLeader=teamLeader)
  

            if request.method == 'GET':
                print("IT'S A GET")
                form = ProjectSearchForm(request.GET)
                print(form)
                if form.is_valid(): 
                    data = form.cleaned_data
                    name = data['name']
                    description = data['description']
                    start_date =data['start_date']
                    end_date =data['end_date']
                    print("ENNDDD DATEEE  ",end_date)
                    projects = Project.objects.filter(Q(teamLeader=teamLeader) 
                                                          & Q(name__icontains= request.GET.get('name')) if request.GET.get('name') else Q() 
                                                        & Q(description__icontains=request.GET.get('description')) if request.GET.get('description') else Q() 
                                                        & Q(start_date__gte= request.GET.get('start_date')) if request.GET.get('start_date') else Q() 
                                                        & Q(end_date__lte=request.GET.get('end_date')) if request.GET.get('end_date') else Q() )
            


            
  
            return render(request, 'manage_projects.html', {  'projects': projects}) 

        except TeamLeader.DoesNotExist:
            print("TeamLeader.DoesNotExist")
        print("FF ", projects_)
    return redirect('login')



def create_project(request):
    form = ProjectForm()
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ProjectForm(request.POST)
            print(form)
            if form.is_valid():
                print("AAA")
                data = form.cleaned_data
                name = data['name']
                description = data['description']
                start_date =data['start_date']
                end_date =data['end_date']
                try:
                    team_leader = TeamLeader.objects.get(user=request.user)
                    project = Project(teamLeader=team_leader, name=name, description=description, start_date=start_date,end_date=end_date)
                    project.save()  
                except TeamLeader.DoesNotExist:
                    print("TeamLeader.DoesNotExist")

                return redirect(manage_projects)
            else:
                return render(request, 'create_project.html')
        return render(request, 'create_project.html', { 'form': form, 'projects': nav_TeamLeader_projects(request)})
    return redirect('login')

def deleteProject(request, id):
    if request.user.is_authenticated:
        project = Project.objects.get(id=id)
        project.delete()
        return HttpResponseRedirect('/manage_projects/')
    return redirect('login')

def editProject(request, id):
    projects_ = []
    try:
        teamLeader = TeamLeader.objects.filter(user=request.user).first()
        projects = Project.objects.filter(teamLeader=teamLeader)
        for project in projects:
            projects_.append(project)
    except TeamLeader.DoesNotExist:
        print("TeamLeader.DoesNotExist")
    #---END navigation----
    if request.user.is_authenticated:
        project = Project.objects.get(id=id)

        if request.method == 'POST':
            form = ProjectForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data['name'] != "":
                    project.name = data['name']
                if data['description'] != "":
                    project.description = data['description']
                if data['start_date'] != "":
                    project.start_date = data['start_date']
                if data['end_date'] != "":
                    project.end_date = data['end_date']
                project.save()
                return redirect(manage_projects) 
        else:
            form = ProjectForm(initial={
                'name': project.name,
                'description': project.description,
                'start_date': project.start_date,
                'end_date': project.end_date,
            })
        return render(request, 'editProject.html', { 'form': form,'projects': nav_TeamLeader_projects(request)})
    return redirect('login')

def results(request):
    if request.user.is_authenticated:
        try:
            teamLeader = TeamLeader.objects.filter(user=request.user).first()

        except TeamLeader.DoesNotExist:
            print("TeamLeader.DoesNotExist")

        projects = Project.objects.filter(teamLeader=teamLeader)
        project_TM_results = {}
        data= []
        project_TM_results_bool  = False   
        for project in projects:
            invitations = Invitations.objects.filter(project=project, accept=True)
            videos = Video.objects.filter(project__id=project.id) 

            data.append(invitations.count()) #0 total tasks with emotion done
            data.append(videos.count()) #0 total tasks with emotion done
            project_TM_results[project]=data
        
        if len(project_TM_results)!=0:
            project_TM_results_bool = True
        return render(request, 'results.html', {'project_TM_results': project_TM_results,
                                                'project_TM_results_bool':project_TM_results_bool, 
                                                'projects': nav_TeamLeader_projects(request)}) 

    return redirect('login')

class Results:
  def __init__(self, name, age):
    self.name = name
    self.age = age

def projectResults(request, projectID):
    if request.user.is_authenticated:
        project = Project.objects.get(id=projectID)
        videos = Video.objects.filter(project__id=projectID) 
        video_results ={}
        for video in videos:
            if SubVideoTask.objects.filter(video = video).exists():
                subVideoTasks = SubVideoTask.objects.filter(video = video)
                dataX= [] # [ [RC, listSmellsEmotion, listSmellsWitouthEmotion ]  ,,,      ]
                emotion_frequency_final = {0: 0, 1: 0, 2: 0, 3: 0, 4:0, 5: 0, 6: 0}

                for subVideoTask in subVideoTasks:

                    new_data = []
                    resultsConsulidation = ResultsConsulidation.objects.get(subVideoTask=subVideoTask)
                    new_data.append(resultsConsulidation)
                    times_freq_dict = json.loads(resultsConsulidation.subVideoTask.emotions_plot_info)

                    print("--------------------------------------------")
                    emotion_frequency = {0: 0, 1: 0, 2: 0, 3: 0, 4:0, 5: 0, 6: 0}

                    for time, emotions_freq in times_freq_dict.items():
                        highest_value_emotion_index = emotions_freq.index(max(emotions_freq))
                        value = emotion_frequency[highest_value_emotion_index]
                        emotion_frequency[highest_value_emotion_index] = value +1
                    
                    emotion_frequency_final[0] = round(emotion_frequency[0]*100 / sum(emotion_frequency.values()),2)
                    emotion_frequency_final[1] = round(emotion_frequency[1]*100 / sum(emotion_frequency.values()),2)
                    emotion_frequency_final[2] = round(emotion_frequency[2]*100 / sum(emotion_frequency.values()),2)
                    emotion_frequency_final[3] = round(emotion_frequency[3]*100 / sum(emotion_frequency.values()),2)
                    emotion_frequency_final[4] = round(emotion_frequency[4]*100 / sum(emotion_frequency.values()),2)
                    emotion_frequency_final[5] = round(emotion_frequency[5]*100 / sum(emotion_frequency.values()),2)
                    emotion_frequency_final[6] = round(emotion_frequency[6]*100 / sum(emotion_frequency.values()),2)

                    x_values = ['Anger', 'Disgust', 'Fear', 'Enjoyment','Contempt', 'Sadness', 'Surprise']
                    y_values = [emotion_frequency_final[0], emotion_frequency_final[1], emotion_frequency_final[2], emotion_frequency_final[3], emotion_frequency_final[4], emotion_frequency_final[5], emotion_frequency_final[6]]
                    colors = ['#A13D3D', '#649941', '#5b3986', '#FF6347','#FFCC66', '#3f6aae','#3DAFAF' ] # list of colors for each bar
                    data = []
                    for i in range(len(x_values)):
                        data.append(
                            go.Bar(
                                x=[x_values[i]],
                                y=[y_values[i]],
                                marker=dict(
                                    color=colors[i]
                                ),
                                name=x_values[i]

                            )
                        )
                

                    layout = go.Layout(
                        title={
                        'text': 'Relative frequency of facial emotions',
                        'x': 0.5, # Center the title
                        'y': 0.85, # set y position closer to plot

                        'xanchor': 'center' # Center the title horizontally
                    },    

                        xaxis=dict(title='Emotion',  tickmode='linear', tickformat='%M'),
                        yaxis=dict(title='Probability of Emotions (%)'),
                        font=dict( size=11),
                    )

                    fig = go.Figure(data=data, layout=layout)
                    div = opy.plot(fig, auto_open=False, output_type='div')
                    smellsWithEmotion_ = []
                    for smellsWithEmotion  in json.loads(resultsConsulidation.usabilitySmells_selected_with_emotion):
                        smellsWithEmotion_.append(smellsWithEmotion)
                    new_data.append(smellsWithEmotion_)

                    smellsWithoutEmotion_ = []
                    for smellsWithoutEmotion in json.loads(resultsConsulidation.usabilitySmells_selected_without_emotion):
                        smellsWithoutEmotion_.append(smellsWithoutEmotion)
                    new_data.append(smellsWithoutEmotion_)
                    new_data.append(div)

                    dataX.append(new_data)
                    emotion_frequency_final.clear()
                print(dataX)
                video_results[video]=dataX


 
        return render(request, 'projectResults.html', {'projectID':projectID, 
                                                       'projectName':project.name,
                                                         'video_results':video_results, 
                                                         'projects': nav_TeamLeader_projects(request)}) 

    return redirect('login')

def resultsConsolidation(request):
    if request.user.is_authenticated:
        try:
            teamLeader = TeamLeader.objects.filter(user=request.user).first()

        except TeamLeader.DoesNotExist:
            print("TeamLeader.DoesNotExist")

        projects = Project.objects.filter(teamLeader=teamLeader)
        project_TM_results = {}
        data= []
        project_TM_results_bool  = False   
        for project in projects:
            invitations = Invitations.objects.filter(project=project, accept=True)
            videos = Video.objects.filter(project__id=project.id) 

            data.append(invitations.count()) #0 total tasks with emotion done
            data.append(videos.count()) #0 total tasks with emotion done
            project_TM_results[project]=data
        
        if len(project_TM_results)!=0:
            project_TM_results_bool = True
        return render(request, 'resultsConsolidation.html', {'project_TM_results': project_TM_results,'project_TM_results_bool':project_TM_results_bool, 'projects': nav_TeamLeader_projects(request)}) 

    return redirect('login')

def resultsConsolidation_permissions(request):
    if request.user.is_authenticated:
        try:
            teamLeader = TeamLeader.objects.filter(user=request.user).first()

        except TeamLeader.DoesNotExist:
            print("TeamLeader.DoesNotExist")

        projects = Project.objects.filter(teamLeader=teamLeader)
        project_TM_results = {}
        data= []
        project_TM_results_bool  = False   
        for project in projects:
            invitations = Invitations.objects.filter(project=project, accept=True)
            videos = Video.objects.filter(project__id=project.id) 

            data.append(invitations.count()) #0 total tasks with emotion done
            data.append(videos.count()) #0 total tasks with emotion done
            project_TM_results[project]=data
        
        if len(project_TM_results)!=0:
            project_TM_results_bool = True
        return render(request, 'resultsConsolidation_permissions.html', {'project_TM_results': project_TM_results,'project_TM_results_bool':project_TM_results_bool, 'projects': nav_TeamLeader_projects(request)}) 

    return redirect('login')



def resultsConsolidation_usabilityTests_permissions(request, projectID):
    if request.user.is_authenticated:
        try:
            teamLeader = TeamLeader.objects.filter(user=request.user).first()

        except TeamLeader.DoesNotExist:
            print("TeamLeader.DoesNotExist")

        project = Project.objects.get(id=projectID)
        project_TM_Videos_results = {}
        project_TM_Videos_results_bool  = False   
        invitations = Invitations.objects.filter(project=project, accept=True)
        videos = Video.objects.filter(project__id=projectID) 
        print(invitations)
        subvideo_data = []

        for invitation in invitations:

                for video in videos:
                    #print("VIDEO ", video)
                    if SubVideoTask.objects.filter(video = video).exists():
                        subVideoTask = SubVideoTask.objects.filter(video = video)  
                        #print(" ****** ", subVideoTask)
                        teamMember = TeamMember.objects.get(id=invitation.teamMember.id)

                        totalTasks_with_emotion = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember= teamMember).count()
                        totalTasks_without_emotion = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember= teamMember).count()

                        #totalTasks = SubVideoTask.objects.filter(video = video).count()
                        totalTasks_done_with_emotions = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,eval_done_with_emotion=True).count()
                        totalTasks_done_without_emotions = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,eval_done_without_emotion=True).count()
                        

                        totalTasks_done_with_emotions_Smells = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,usabilitySmells_done_with_emotion=True).count()
                        totalTasks_done_without_emotions_Smells = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,usabilitySmells_done_without_emotion=True).count()
                        
                        data= []

                        data.append(teamMember) #0
                        data.append(subVideoTask) #1 
                        data.append(totalTasks_with_emotion) #2 
                        data.append(totalTasks_without_emotion) #3
                        data.append(totalTasks_done_with_emotions) #4
                        data.append(totalTasks_done_without_emotions) #5 
                        data.append(totalTasks_done_with_emotions_Smells) #6 
                        data.append(totalTasks_done_without_emotions_Smells) #7 
                        data.append(video) #8
                        if ResultsConsulidationPermission.objects.filter(video=video).exists():
                            print("TRUEEEE -----")
                            data.append(True) #9
                        else:
                            data.append(False) #9


                        #print("DATA " ,data)
                        subvideo_data.append(data)
                        #print("====", subvideo_data)


                    project_TM_Videos_results[video]=subvideo_data 
                #print("-------- ", project_TM_Videos_results)
      
        #project_TM_Videos_results = {k: v for k, v in project_TM_Videos_results.items() if k in v[0]}
        print(len(project_TM_Videos_results))
              
              
        x = {}
        for k, v in project_TM_Videos_results.items():
            new_v = [sublist for sublist in v if k in sublist]
            x[k] = new_v
        print(len(project_TM_Videos_results))


        #print(project_TM_Videos_results)
        if len(project_TM_Videos_results)!=0:
            project_TM_Videos_results_bool = True
        return render(request, 'resultsConsolidation_usabilityTests_permissions.html', {'projectID':projectID, 'projectName':project.name, 'project_TM_Videos_results': x,'project_TM_Videos_results_bool':project_TM_Videos_results_bool, 'projects': nav_TeamLeader_projects(request)}) 

    return redirect('login')

def allow_TM_resultsConsolidation(request, videoID):
    if request.user.is_authenticated:
        video = Video.objects.get(id=videoID)
        resultsConsulidatioPermission = ResultsConsulidationPermission.objects.create(video=video, allow_permission=True)
        resultsConsulidatioPermission.save()
        return HttpResponseRedirect('/resultsConsolidation_usabilityTests_permissions/' + str(video.project.id))
    return redirect('login')

def not_allow_TM_resultsConsolidation(request, videoID):
    if request.user.is_authenticated:
        video = Video.objects.get(id=videoID)
        resultsConsulidatioPermission = ResultsConsulidationPermission.objects.filter(video=video)
        print(resultsConsulidatioPermission)
        resultsConsulidatioPermission.delete()
        return HttpResponseRedirect('/resultsConsolidation_usabilityTests_permissions/' + str(video.project.id))
    return redirect('login')


def resultsConsolidation_usabilityTests(request, projectID):
    if request.user.is_authenticated:
        try:
            teamLeader = TeamLeader.objects.filter(user=request.user).first()

        except TeamLeader.DoesNotExist:
            print("TeamLeader.DoesNotExist")

        project = Project.objects.get(id=projectID)
        project_TM_Videos_results = {}
        project_TM_Videos_results_bool  = False   
        invitations = Invitations.objects.filter(project=project, accept=True)
        videos = Video.objects.filter(project__id=projectID) 
        print(invitations)
        subvideo_data = []

        for invitation in invitations:

                for video in videos:
                    #print("VIDEO ", video)
                    if SubVideoTask.objects.filter(video = video).exists():
                        subVideoTask = SubVideoTask.objects.filter(video = video)  
                        #print(" ****** ", subVideoTask)
                        teamMember = TeamMember.objects.get(id=invitation.teamMember.id)

                        totalTasks_with_emotion = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember= teamMember).count()
                        totalTasks_without_emotion = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember= teamMember).count()

                        #totalTasks = SubVideoTask.objects.filter(video = video).count()
                        totalTasks_done_with_emotions = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,eval_done_with_emotion=True).count()
                        totalTasks_done_without_emotions = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,eval_done_without_emotion=True).count()
                        

                        totalTasks_done_with_emotions_Smells = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,usabilitySmells_done_with_emotion=True).count()
                        totalTasks_done_without_emotions_Smells = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask__in=subVideoTask, teamMember = teamMember,usabilitySmells_done_without_emotion=True).count()
                        
                        data= []

                        data.append(teamMember) #0
                        data.append(subVideoTask) #1 
                        data.append(totalTasks_with_emotion) #2 
                        data.append(totalTasks_without_emotion) #3
                        data.append(totalTasks_done_with_emotions) #4
                        data.append(totalTasks_done_without_emotions) #5 
                        data.append(totalTasks_done_with_emotions_Smells) #6 
                        data.append(totalTasks_done_without_emotions_Smells) #7 
                        data.append(video) #8

                        #print("DATA " ,data)
                        subvideo_data.append(data)
                        #print("====", subvideo_data)


                    project_TM_Videos_results[video]=subvideo_data 
                #print("-------- ", project_TM_Videos_results)
      
        #project_TM_Videos_results = {k: v for k, v in project_TM_Videos_results.items() if k in v[0]}
        print(len(project_TM_Videos_results))
              
              
        x = {}
        for k, v in project_TM_Videos_results.items():
            new_v = [sublist for sublist in v if k in sublist]
            x[k] = new_v
        print(len(project_TM_Videos_results))


        #print(project_TM_Videos_results)
        if len(project_TM_Videos_results)!=0:
            project_TM_Videos_results_bool = True
        return render(request, 'resultsConsolidation_usabilityTests.html', {'projectID':projectID, 'projectName':project.name, 'project_TM_Videos_results': x,'project_TM_Videos_results_bool':project_TM_Videos_results_bool, 'projects': nav_TeamLeader_projects(request)}) 

    return redirect('login')

def resultsConsolidation_TM_evaluation(request,evalType, videoID):
    if request.user.is_authenticated:

        video = Video.objects.get(id = videoID)  
        project = Project.objects.get(id = video.project.id)  
        subVideoTasks = SubVideoTask.objects.filter(video = video)  
        results = {}
        if evalType == "CW_with_emotion":
            for subVideoTask in subVideoTasks:
                data = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask = subVideoTask) 
                data = list(data) + list(ResultsConsulidation.objects.filter(subVideoTask = subVideoTask))
                results[subVideoTask] = data
        elif evalType == "CW_without_emotion":
            for subVideoTask in subVideoTasks:
                data = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask = subVideoTask)  
                data = list(data) + list(ResultsConsulidation.objects.filter(subVideoTask = subVideoTask))

                results[subVideoTask] = data

        elif evalType == "Smells_with_emotion":
            for subVideoTask in subVideoTasks:
                data = UsabilityEval_CW_Smells_Emotion.objects.filter(subVideoTask = subVideoTask)  
                new_data = []
                for d in data:
                    new_data.append(d.teamMember)
                    new_data.append(json.loads(d.usabilitySmells_selected_with_emotion))
                    new_data.append(d.usabilitySmells_notes_with_emotion)
                    new_data.append(d.usabilitySmells_notes_with_emotion)
                
                print(" ==================== ",new_data)
                results[subVideoTask] = new_data

        elif evalType == "Smells_without_emotion":
            for subVideoTask in subVideoTasks:
                data = UsabilityEval_CW_Smells_without_Emotion.objects.filter(subVideoTask = subVideoTask)  
                new_data = []
                for d in data:
                    new_data.append(d.teamMember)
                    new_data.append(json.loads(d.usabilitySmells_selected_without_emotion))
                    new_data.append(d.usabilitySmells_notes_without_emotion)
                results[subVideoTask] = new_data

        print(results)
       
        return render(request, 'resultsConsolidation_TM_evaluation.html', {'projectID':project.id, 'projectName':project.name, 
                                                                           'results': results,
                                                                           'evalType':evalType, 'projects': nav_TeamLeader_projects(request)}) 

    return redirect('login')



def manage_Invitations(request):
    invitations_ = []
    if request.user.is_authenticated:
        invitations_ = []
  
        invitationsBool = False
        try:
            teamLeader = TeamLeader.objects.filter(user=request.user).first()
        except TeamLeader.DoesNotExist:
            print("TeamLeader.DoesNotExist")

        if request.method == 'GET':
            print("IF -------------------------")
            form = InvitationSearchForm(request.POST)
            print(form)
            if form.is_valid():
                print("IS VALID")
                projects = Project.objects.filter(teamLeader=teamLeader)
                for project in projects:
                    invitations = Invitations.objects.filter(Q(project=project)
                                                    & Q(project__name__icontains= request.GET.get('proj_name')) if request.GET.get('proj_name') else Q() 
                                                    & Q(teamMember__user__first_name__icontains=request.GET.get('member_name')) if request.GET.get('member_name') else Q() 
                                                    & Q(teamMember__user__email__icontains= request.GET.get('teamMemberEmail')) if request.GET.get('teamMemberEmail') else Q() 
                                                    & Q(project__start_date__gte= request.GET.get('start_date')) if request.GET.get('start_date') else Q() 
                                                    & Q(project__end_date__lte=request.GET.get('end_date')) if request.GET.get('end_date') else Q() 
                                                    & Q(created_at__eq=request.GET.get('created_at')) if request.GET.get('created_at') else Q() )
                    for invitation in invitations:
                        invitations_.append(invitation)
        else:
            print("ELSE -------------------------")

            projects = Project.objects.filter(teamLeader=teamLeader)
            for project in projects:
                invitations = Invitations.objects.filter(project=project)

                for invitation in invitations:
                    invitations_.append(invitation)
            

        if len(invitations_)!=0:
            invitationsBool = True
        print(invitations_)

        return render(request, 'manage_Invitations.html', {'invitations': set(invitations_), 'invitationsBool':invitationsBool,'projects': nav_TeamLeader_projects(request)}) 
    return redirect('login')


def create_Invitations(request):
    form = InvitationForm()
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = InvitationForm(request.POST)
            if form.is_valid():
                print("AAA")
                data = form.cleaned_data
                projectID = data['projectID']
                teamMemberEmail = data['teamMemberEmail']
                if TeamMember.objects.filter(user__email=teamMemberEmail).exists():
                    if 'projectID' in request.POST:
                        projectIDs = request.POST.getlist('projectID', [])
                        print("--- projectIDs ", projectIDs)
                        #options selected inside list
                        for projectID in projectIDs:
                            #if len(Invitations.objects.filter(project__id=projectID)) == 0:
                            print("EMAIL ", teamMemberEmail)

                            invitation = Invitations.objects.create(project=Project.objects.get(id=int(projectID)), 
                                                    teamMember=TeamMember.objects.get(user__email=teamMemberEmail), 
                                                    accept=False)
                            print("...>>>>> ", invitation) 
                            invitation.save() 
                        return redirect(manage_Invitations)
                else:
                    return render(request, 'create_Invitations.html', { 'form': form,'projects': nav_TeamLeader_projects(request), 'error': "User email does not exists. Enter a valid user email that there's in the database."})
        return render(request, 'create_Invitations.html', { 'form': form, 'projects': nav_TeamLeader_projects(request)})
    return redirect('login')

def deleteInvitation(request, id):
    if request.user.is_authenticated:
        invitation = Invitations.objects.get(id=id)
        invitation.delete()
        return HttpResponseRedirect('/manage_Invitations/')
    return redirect('login')









def editUserTasks(request, id):
    pageID = id
    subvideosBool = False
    if request.user.is_authenticated:
        subVideo_by_userUID = SubVideoTask.objects.filter(video__id=id)
        subVideos_dict={}
        for sV in subVideo_by_userUID:
            data= []
            data.append(sV.created_at) #0

            data.append(sV.task_number) #1
            
            actions_ = []
            actions = sV.actions.split("#")
            for action in actions:
                actions_.append(action)
            data.append(actions_)     #2
            
            usabilitySmells_ = []
            usabilitySmells = sV.usabilitySmells.split("#")
            for uS in usabilitySmells:
                usabilitySmells_.append(uS)
            data.append(usabilitySmells_)     #3            
            
            data.append(sV.screen_sub_video_emotions) #4

            subVideos_dict[sV.id]=data
        print(subVideos_dict)

        if len(subVideos_dict) != 0:
            subvideosBool = True
        return render(request, 'editUserTasks.html', {'subvideosBool':subvideosBool, 'videoID':id , 'subVideos_dict':subVideos_dict, 'pageID': pageID,'projects': nav_TeamLeader_projects(request)})
    else:
        return redirect('login')



def CW_editUserTask(request, id):
    pageID = id
    if request.user.is_authenticated:
        subVideoTask = SubVideoTask.objects.get(id=id)
        pagevideoID = SubVideoTask.objects.get(id=id).video.id

        if request.method == 'POST':
            form = EditSubVideoTaskForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data['task_number'] != "":
                    subVideoTask.task_number = data['task_number']
                if data['actions'] != "":
                    subVideoTask.actions = data['actions']
                subVideoTask.save()
                return redirect(manageTestingVideos) 
        else:
            form = EditSubVideoTaskForm(initial={
                'task_number': subVideoTask.task_number,
                'actions': subVideoTask.actions,
            })
        return render(request, 'CW_editUserTask.html', {'projects': nav_TeamLeader_projects(request), 'plot':emotion_dict_to_plot(subVideoTask.emotions_plot_info), 'form': form, 'pagevideoID': pagevideoID, 'projects': nav_TeamLeader_projects(request),'pageID': pageID, 'screen_sub_video_emotions': subVideoTask.screen_sub_video_emotions, 'screen_sub_video_sem_emotions': subVideoTask.screen_sub_video_sem_emotions})
    return redirect('login')

def Smells_editUserTask(request, id):
    pageID = id
    if request.user.is_authenticated:
        subVideoTask = SubVideoTask.objects.get(id=id)
        pagevideoID = SubVideoTask.objects.get(id=id).video.id

        if request.method == 'POST':
            form = EditSubVideoTaskForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data['task_number'] != "":
                    subVideoTask.task_number = data['task_number']
                if data['usabilitySmells'] != "":
                    subVideoTask.usabilitySmells = data['usabilitySmells']
                subVideoTask.save()
                return redirect(manageTestingVideos) 
        else:
            form = EditSubVideoTaskForm(initial={
                'task_number': subVideoTask.task_number,
                'usabilitySmells': subVideoTask.usabilitySmells,
            })
        return render(request, 'Smells_editUserTask.html', {'projects': nav_TeamLeader_projects(request),'plot':emotion_dict_to_plot(subVideoTask.emotions_plot_info), 'form': form, 'pagevideoID': pagevideoID, 'pageID': pageID, 'screen_sub_video_emotions': subVideoTask.screen_sub_video_emotions, 'screen_sub_video_sem_emotions': subVideoTask.screen_sub_video_sem_emotions})
    return redirect('login')

def deleteTask(request, id, idVideo):
    if request.user.is_authenticated:
        subVideoTask = SubVideoTask.objects.get(id=id)
        subVideoTask.delete()
        return HttpResponseRedirect('/editUserTasks/'+ str(idVideo))

    return redirect('login')



def usabilityTestUpload(request):
    if request.user.is_authenticated:
        form = VideoForm()
        if request.method == 'POST':
            form = VideoForm(request.POST, request.FILES)
            if form.is_valid():
                print(form.cleaned_data)



                video_file = request.FILES['webcam_video']
                screen_video = request.FILES['screen_video']
                #screen_emotions_video = request.FILES['screen_emotions_video']

                #formatar o video das expressões faciais para o algoritmo CNN
                video_path = os.path.dirname(__file__) + '/' + video_file.name
                with open(video_path, 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                
                #formatar o video do screen para o algoritmo CNN
                video_path_screen = os.path.dirname(__file__) + '/' + screen_video.name
                with open(video_path_screen, 'wb+') as dest:
                    for chunk in screen_video.chunks():
                        dest.write(chunk)


                #Obter as facial emotions
                _, emotion_plot = get_emotions_dict_and_save_video(video_path, video_path_screen)
                
                #Video originado do algoritmo
                emotions_video_location = os.path.dirname(__file__)[:-4] + '/' + 'emotions_' + video_file.name
                screen_emotions_video_location = os.path.dirname(__file__)[:-4] + '/' + 'screen_emotions_' +screen_video.name

                #Video do algoritmo para formato mp4 compativel
                convert_to_mp4(emotions_video_location, emotions_video_location)
                convert_to_mp4(screen_emotions_video_location, screen_emotions_video_location)

                if request.POST.get('project', False):
                    print(request.POST.get('project', False))
                    new_video = Video.objects.create(project = Project.objects.filter(id=int(request.POST.get('project', False))).first(),
                                                    usability_test_name = str(form.cleaned_data['usability_test_name']),
                                                    user_type = str(form.cleaned_data['user_type']),
                                                    user_UID = form.cleaned_data['user_UID'], 
                                                    local = str(form.cleaned_data['local']), 
                                                    webcam_video=file_to_memory(emotions_video_location[:-4] + "_conv.mp4"),
                                                    screen_video = file_to_memory(video_path_screen), 
                                                    screen_emotions_video = file_to_memory(screen_emotions_video_location[:-4] + "_conv.mp4"), 
                                                    emotions_plot_info = json.dumps(emotion_plot) )

                    new_video.save()


                os.remove(emotions_video_location[:-4] + "_conv.mp4")
                os.remove(emotions_video_location)
                os.remove(screen_emotions_video_location[:-4] + "_conv.mp4")
                os.remove(screen_emotions_video_location)
                os.remove(video_path_screen)

                return render(request, 'usabilityTestUpload.html', {'projects': nav_TeamLeader_projects(request),'message': "Video uploaded successfully."})
            else:
                return render(request, 'usabilityTestUpload.html', {'projects': nav_TeamLeader_projects(request),'form': form, 'video': Video.objects.last()})

        else:
            print(nav_TeamLeader_projects(request))
            return render(request, 'usabilityTestUpload.html', {'projects': nav_TeamLeader_projects(request),'form': form, 'video': Video.objects.last()})
    else:
        return redirect('login')

#------------------------------------------------------------------------------------------------------------------------------------------------------
#manage testing videos
def manageTestingVideos(request):
    if request.user.is_authenticated:
        videos_dict = {}
        #Current Team leader videos only
        teamLeader = TeamLeader.objects.filter(user=request.user).first()
        if request.method == 'GET':
                print("GET")
                form = selectVideoSearchForm(request.POST)
                if form.is_valid():
                    print("IS VALID")
                    data = form.cleaned_data
                    print("DATA :D  "  , data)
                    if request.GET.get('proj_name') :
                        print(request.GET.get('usability_test_name'))
                        print("TRUE----")
                        projects = Project.objects.filter(Q(teamLeader=teamLeader) & Q(name__icontains=request.GET.get('proj_name')) if request.GET.get('proj_name') else Q()  )
                        print("PROJECTS  ",projects)
                        if len(projects) !=0:
                            for project in projects:
                                videos = Video.objects.filter(Q(project=project) 
                                                            & Q(usability_test_name__icontains= request.GET.get('usability_test_name')) if request.GET.get('usability_test_name') else Q() 
                                                            & Q(user_type__icontains=request.GET.get('user_type')) if request.GET.get('user_type') else Q() 
                                                            & Q(user_UID__icontains= request.GET.get('user_UID')) if request.GET.get('user_UID') else Q() 
                                                            & Q(local__icontains=request.GET.get('local')) if request.GET.get('local') else Q() )
                                print("VIDEOS  ", videos)
                                for video in videos:
                                    print("splited_bool ", request.POST.getlist('splited_bool', []))
                                    if len(request.GET.getlist('splited_bool', []))  != 0:
                                        value = request.GET.getlist('splited_bool', [])[0]
                                        if value == "Yes":
                                            if SubVideoTask.objects.filter(video = video).exists():
                                                videos_dict[video] = True
                                        else:
                                            if not SubVideoTask.objects.filter(video = video).exists():
                                                videos_dict[video] = False
                                    else:
                                        if SubVideoTask.objects.filter(video = video).exists():
                                            videos_dict[video] = True
                                        else:
                                            if not SubVideoTask.objects.filter(video = video).exists():
                                                videos_dict[video] = False
                        

                    else:
                        print(request.GET.get('usability_test_name'))
                        print("NO PROJECT NAME")
                        projects = Project.objects.filter(teamLeader=teamLeader)
                        for project in projects:
                            videos = Video.objects.filter(Q(project=project) 
                                                            & Q(usability_test_name__icontains= request.GET.get('usability_test_name')) if request.GET.get('usability_test_name') else Q() 
                                                            & Q(user_type__icontains=request.GET.get('user_type')) if request.GET.get('user_type') else Q() 
                                                            & Q(user_UID= request.GET.get('user_UID')) if request.GET.get('user_UID') else Q() 
                                                            & Q(local__icontains=request.GET.get('local')) if request.GET.get('local') else Q() )
                            print("VIDEOS  ", videos)

                            for video in videos:
                                print("TTT", video.user_UID)
                                if len(request.GET.getlist('splited_bool', []))  != 0:
                                    value = request.GET.getlist('splited_bool', [])[0]
                                    if value == "Yes":
                                        print("YES ---")
                                        if SubVideoTask.objects.filter(video = video).exists():
                                            videos_dict[video] = True
                                    else:
                                        if not SubVideoTask.objects.filter(video = video).exists():
                                            videos_dict[video] = False
                                else:
                                    if SubVideoTask.objects.filter(video = video).exists():
                                        videos_dict[video] = True
                                    else:
                                        if not SubVideoTask.objects.filter(video = video).exists():
                                            videos_dict[video] = False

        else:
            print("ISN'T VALID")

            projects = Project.objects.filter(teamLeader=teamLeader)

            videos = []
            for project in projects:
                project_videos = Video.objects.filter(project=project)
                for project_video in project_videos:
                    videos.append(project_video)
            
            for video in videos:
                if SubVideoTask.objects.filter(video = video).exists():
                    videos_dict[video] = True
                else:
                    videos_dict[video] = False
            print("FINAL VIDEOS ", videos_dict)
        return render(request, 'manageTestingVideos.html', {'projects': nav_TeamLeader_projects(request),'videos_dict': videos_dict}) 
    return redirect('login')

def deleteVideo(request, id):
    if request.user.is_authenticated:
        video = Video.objects.get(id=id)
        video.delete()
        return HttpResponseRedirect('/manageTestingVideos/')

    return redirect('login')


def updateVideo(request, id):
    if request.user.is_authenticated:
        video = Video.objects.get(id=id)
        if request.method == 'POST':
            form = VideoEditForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data['usability_test_name'] != "":
                    video.usability_test_name = data['usability_test_name']
                if data['user_type'] != "":
                    video.user_type = data['user_type']
                if data['user_UID'] != None:
                    video.user_UID = data['user_UID']
                if data['local'] != "":
                    video.local = data['local']
                video.save()
                return redirect(manageTestingVideos) 
        else:
            form = VideoEditForm(initial={
                'usability_test_name': video.usability_test_name,
                'user_type': video.user_type,
                'user_UID': video.user_UID, 
                'local': video.local,
            })
        return render(request, 'updateVideo.html', {'projects': nav_TeamLeader_projects(request),'form': form, 'video': video.screen_emotions_video})
    return redirect('login')


#------------------------------------------------------------------------------------------------------------------------------------------------------

#selecionar o video que se quer dar split por tasks
def selectVideoToSplit(request):
    if request.user.is_authenticated:
        videos_dict = {}
        print("videos_dict	", videos_dict)
        #Current Team leader videos only
        teamLeader = TeamLeader.objects.filter(user=request.user).first()
        print("AQUI")
        #search bar
        if request.method == 'GET':
            print("GET")
            form = selectVideoSearchForm(request.POST)
            if form.is_valid():
                print("IS VALID")
                data = form.cleaned_data
                print("DATA :D  "  , data)
                if request.GET.get('proj_name') :
                    print(request.GET.get('usability_test_name'))
                    print("TRUE----")
                    projects = Project.objects.filter(Q(teamLeader=teamLeader) & Q(name__icontains=request.GET.get('proj_name')) if request.GET.get('proj_name') else Q()  )
                    print("PROJECTS  ",projects)
                    if len(projects) !=0:
                        for project in projects:
                            videos = Video.objects.filter(Q(project=project) 
                                                          & Q(usability_test_name__icontains= request.GET.get('usability_test_name')) if request.GET.get('usability_test_name') else Q() 
                                                        & Q(user_type__icontains=request.GET.get('user_type')) if request.GET.get('user_type') else Q() 
                                                        & Q(user_UID__icontains= request.GET.get('user_UID')) if request.GET.get('user_UID') else Q() 
                                                        & Q(local__icontains=request.GET.get('local')) if request.GET.get('local') else Q() )
                            print("VIDEOS  ", videos)
                            for video in videos:
                                print("splited_bool ", request.POST.getlist('splited_bool', []))
                                if len(request.GET.getlist('splited_bool', []))  != 0:
                                    value = request.GET.getlist('splited_bool', [])[0]
                                    if value == "Yes":
                                        if SubVideoTask.objects.filter(video = video).exists():
                                            videos_dict[video] = True
                                    else:
                                        if not SubVideoTask.objects.filter(video = video).exists():
                                            videos_dict[video] = False
                                else:
                                    if SubVideoTask.objects.filter(video = video).exists():
                                        videos_dict[video] = True
                                    else:
                                        if not SubVideoTask.objects.filter(video = video).exists():
                                            videos_dict[video] = False
                    

                else:
                    print(request.GET.get('usability_test_name'))
                    print("NO PROJECT NAME")
                    projects = Project.objects.filter(teamLeader=teamLeader)
                    for project in projects:
                        videos = Video.objects.filter(Q(project=project) 
                                                        & Q(usability_test_name__icontains= request.GET.get('usability_test_name')) if request.GET.get('usability_test_name') else Q() 
                                                        & Q(user_type__icontains=request.GET.get('user_type')) if request.GET.get('user_type') else Q() 
                                                        & Q(user_UID= request.GET.get('user_UID')) if request.GET.get('user_UID') else Q() 
                                                        & Q(local__icontains=request.GET.get('local')) if request.GET.get('local') else Q() )
                        print("VIDEOS  ", videos)

                        for video in videos:
                            print("TTT", video.user_UID)
                            if len(request.GET.getlist('splited_bool', []))  != 0:
                                value = request.GET.getlist('splited_bool', [])[0]
                                if value == "Yes":
                                    print("YES ---")
                                    if SubVideoTask.objects.filter(video = video).exists():
                                        videos_dict[video] = True
                                else:
                                    if not SubVideoTask.objects.filter(video = video).exists():
                                        videos_dict[video] = False
                            else:
                                if SubVideoTask.objects.filter(video = video).exists():
                                    videos_dict[video] = True
                                else:
                                    if not SubVideoTask.objects.filter(video = video).exists():
                                        videos_dict[video] = False

        else:
            print("ISN'T VALID")

            projects = Project.objects.filter(teamLeader=teamLeader)

            videos = []
            for project in projects:
                project_videos = Video.objects.filter(project=project)
                for project_video in project_videos:
                    videos.append(project_video)
            
            for video in videos:
                if SubVideoTask.objects.filter(video = video).exists():
                    videos_dict[video] = True
                else:
                    videos_dict[video] = False
            print("FINAL VIDEOS ", videos_dict)

        return render(request, 'selectVideoToSplit.html', {'projects': nav_TeamLeader_projects(request),
                                                           'videos_dict': videos_dict}) 
    return redirect('login')

#obter o video selecionado para dar split
def selectedVideoToSplit(request, id):
    video = Video.objects.filter(id=id)
    video_dict={}
    if request.user.is_authenticated:
        for v in video:
            data= []
            data.append(v.usability_test_name) #0
            data.append(v.user_type)  #1
            data.append(v.user_UID)     #2
            data.append(v.local) #3
            data.append(v.webcam_video) #4
            data.append(v.screen_video) #5
            data.append(v.screen_emotions_video) #6
            data.append(v.id) #7
            video_dict[emotion_dict_to_plot(v.emotions_plot_info)]=data
        return render(request, 'selectedVideoToSplit.html', {'projects': nav_TeamLeader_projects(request),'video_dict': video_dict})
    return redirect('login')


def splitVideo(request):
    form = SelectVideoForm()
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = SelectVideoForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                video = data['video']
                video = Video.objects.get(id=video.id)
                return render(request, 'splitVideo.html', {'projects': nav_TeamLeader_projects(request), 'video': video})
            else:
                return render(request, 'selectVideo.html')
        return render(request, 'selectVideo.html', { 'projects': nav_TeamLeader_projects(request),'form': form})
    return redirect('login')

#Obter informação tabelada com os tempos das tasks, actions... e guardar em SubVideoTask
def videoSplitSubvideos(request):
    times_list = []
    if request.method == 'POST':
        print("ENTROU ...")
        data = json.loads(request.body)
        print(data)
        video_path = data[0]['video']

        video_path = str(video_path).split('/')[-1]
        index = 0
        actions_list_  = []
        usabilitySmells_ = []
        for times in data:
            actions_list_.append(data[index]['actions'])
            usabilitySmells_.append(data[index]['usabilitySmells'])

            time_ = data[index]['time1'].split("-")
            time1 = time_[0].split(":")
            time2 = time_[1].split(":")

            total_seconds1 = int(time1[0].strip()) * 60 + int(time1[1].strip())
            total_seconds2 = int(time2[0].strip()) * 60 + int(time2[1].strip())

            times_list.append(total_seconds1)
            times_list.append(total_seconds2)
            index +=1
        print(times_list)
        
        times_to_split_alg = []

        for i in range(0, len(times_list), 2):
            times_to_split_alg.append(times_list[i:i+2])

        print(times_to_split_alg)


        print("FFFF  ", os.path.dirname(__file__))
        video = Video.objects.get(screen_emotions_video__contains=video_path)
        #video_sem_emotion = Video.objects.get(screen_video__contains=video_path)
        print(">>> video ", video.screen_emotions_video)
        video_path = os.path.dirname(__file__)[:-4] + '/media/' + str(video.screen_emotions_video)
        video_sem_emotion_path = os.path.dirname(__file__)[:-4] + '/media/' + str(video.screen_video)

        print(">>> VIDEO PATH >>>> ", video_path)
        print("EMOTIONS PLOT ", json.loads(video.emotions_plot_info))

        if SubVideoTask.objects.filter(video__user_UID=video.user_UID).exists():
            SubVideoTask.objects.filter(video__user_UID=video.user_UID).delete()
        else:
            task_number = 1
            index = 0
            for t in times_to_split_alg:
                split_video_range_time(video_path, math.floor(t[0]), math.floor(t[1]), "c_emotions.mp4")
                split_video_range_time(video_sem_emotion_path, math.floor(t[0]), math.floor(t[1]), "sem_emotions.mp4")

                SubVideoTask(user= request.user,task_number=task_number, video=video, screen_sub_video_emotions= file_to_memory(os.path.dirname(__file__)[:-4] + "/c_emotions.mp4"),
                             screen_sub_video_sem_emotions=file_to_memory(os.path.dirname(__file__)[:-4] + "/sem_emotions.mp4"),  
                             actions = actions_list_[index],
                             emotions_plot_info=json.dumps(filter_dict_by_time(json.loads(video.emotions_plot_info), 
                             math.floor(t[0])*1000, math.floor(t[1])*1000)),
                             usabilitySmells =usabilitySmells_[index]).save()
                os.remove(os.path.dirname(__file__)[:-4] + "/c_emotions.mp4")
                os.remove(os.path.dirname(__file__)[:-4] + "/sem_emotions.mp4")

                task_number +=1
                index +=1
    return JsonResponse({'message': 'Success'})



def home(request):
    if request.user.is_authenticated:
        projectBool, projects= nav_TeamMember_projects(request)

        return render(request, 'home.html', {'projectBool':projectBool,'projects_':projects, 'projects': nav_TeamLeader_projects(request)})
    else:
        return render(request, 'home.html', {})


#USER STUF
def logout(request):
    logoutUser(request)
    return redirect('home')

def login(request):

    if not TeamMember.objects.filter(user__email = "x2xxx123@gmail.com"):
        user = User.objects.create_user(username="x2xxx123", first_name="x2xxx123",last_name="x2xxx123", email="x2xxx123@gmail.com",password="@asfdsgsc2123" )
        TeamMember.objects.create(user=user).save()

    if request.user.is_authenticated:
        return redirect('home')
    else:
        logoutUser(request)

        if request.method == 'POST':
            username = request.POST.get('user')
            password = request.POST.get('pass')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                loginUser(request, user)
                messages.success(request,'Welcome  {}!'.format(user.username))
                
                    
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')
        context = {}
        return render(request, 'login.html', context) 

#super_user = TeamLeader
def signup(request):

    if request.user.is_authenticated:
        messages.info(request, 'You are already registered')
        return redirect('home')
    else:
        logoutUser(request)


        print("HERE")
        form = newUserForm()
        if request.method == 'POST':
            form = newUserForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                print(data)
                username = data['username']
                email = data['email']
                firstName = data['first_name']
                lastName = data['last_name']
                password1 = data['password1']
                password2 = data['password2']
                user = User.objects.create_user(username=username, first_name=firstName,last_name=lastName, email=email,password=password1 )               
                if request.POST.get('teamLeader', False):
                    user.staff = True
                    user.is_superuser = True
                    user.save()
                    TeamLeader(user = user).save()
                else:
                    user.staff = False
                    user.is_superuser = False
                    user.save()
                    TeamMember(user = user).save()

                #
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                return redirect('login')
        return render(request, 'signup.html', {'form': form})
    
def account(request):
    tparams = {}
    if request.user.is_authenticated:
        projectBool, projects= nav_TeamMember_projects(request)

        teamLeader = TeamLeader.objects.filter(user=request.user).first()
        teamMember = TeamMember.objects.filter(user=request.user).first()
        user_profile = None
        if teamLeader != None:
            user_profile =teamLeader
        elif teamMember != None:
            user_profile =teamMember
        if request.method == 'POST':
            form = updateUserForm(request.POST)


            if form.is_valid():
                print("SIMM")
                data = form.cleaned_data
                print(data)
                username = data['username']
                email = data['email']
                curPass = data['currentPassword']
                firstName = data['first_name']
                lastName = data['last_name']
                if request.user.check_password(curPass):
                    
                    user = request.user
                    if username != "":
                        user.username = username
                    if firstName != "":
                        user.first_name = firstName
                    if lastName != "":
                        user.last_name = lastName
                    if email != "":
                        user.email = email
                    if request.FILES['avatar'] != None:
                        if user_profile != None:
                            user_profile.avatar = request.FILES['avatar']
                            user_profile.save()
             

                    user.save()
                    messages.success(request, 'Username with name  {}  added.'.format(username))
            else:
                print("NAOOOO")
                form = updateUserForm()
                tparams['form'] = form
                tparams['projects'] = nav_TeamLeader_projects(request)

            return render(request, 'account.html',  {'tparams': tparams, 'projectBool':projectBool,'projects_':projects,})
        else:
            initial = { 'first_name':request.user.first_name,
                        'last_name': request.user.last_name,
                        'username':request.user.username,
                        'email': request.user.email,
                        'currentPassword': request.user.password,
                      
                       }
            form = updateUserForm(initial=initial)

        #tparams['form'] = form
        #tparams['user_profile_avatar'] = user_profile.avatar

        #tparams['projects'] = nav_TeamLeader_projects(request)

        return render(request, 'account.html',  {'form': form,'projects':nav_TeamLeader_projects(request), 'projectBool':projectBool,'projects_':projects, })
    return redirect('login')

  