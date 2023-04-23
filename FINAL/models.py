from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

"""
One-To-Many

Reporter -> N Articles
            reporter FK

"""
class TeamLeader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #superuser
    def __str__(self):
        return str(self.user.username)


class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 

    def __str__(self):
        return str(self.user.username)
    
class Project(models.Model):
    teamLeader = models.ForeignKey(TeamLeader, default=None, on_delete=models.CASCADE)
    name = models.CharField(max_length=99999,default="x")
    description = models.CharField(max_length=99999,default="x")
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(default=datetime.now, blank=False)
    end_date = models.DateTimeField(default=datetime.now,blank=False)
    def __str__(self):
        return self.name

class UsabilitySmells(models.Model):
    teamLeader = models.ForeignKey(TeamLeader, default=None, on_delete=models.CASCADE)
    usabilitySmell = models.CharField(max_length=99999999,default="x")
    description = models.CharField(max_length=99999,default="x")
    def __str__(self):
        return "UsabilitySmells - " +str(self.teamLeader.user.username)

class HeuristicEvaluation(models.Model):
    teamLeader = models.ForeignKey(TeamLeader, default=None, on_delete=models.CASCADE)
    heuristicName = models.CharField(max_length=99999999,default="x")
    description = models.CharField(max_length=99999,default="x")
    def __str__(self):
        return "HeuristicEvaluation - " +str(self.teamLeader.user.username)

     
class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=None)
    usability_test_name = models.CharField(max_length=300, blank=True, null=True)
    user_type = models.CharField(max_length=300,blank=True, null=True)
    user_UID = models.IntegerField(blank=True, null=True) 
    local = models.CharField(max_length=300, blank=True, null=True)
    webcam_video=models.FileField(upload_to="videos/")
    screen_video=models.FileField(upload_to="videos/")
    screen_emotions_video=models.FileField(upload_to="videos/")
    emotions_plot_info = models.CharField(max_length=999999999999999, blank=True, null=True)
    def __str__(self):
        return "Usability_test_name: " + str(self.usability_test_name)+ " Project: " + str(self.project.name)

#buscar o invitation.project == video.project
#            "Vários"
class Invitations(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE,default=None)
    teamMember = models.ForeignKey(TeamMember, on_delete=models.CASCADE,default=None)
    accept =  models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "teamMember: " + str(self.teamMember.user.username) + " Project: " + str(self.project.name)
    
class ResultsConsulidationPermission(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE,default=None)
    allow_permission =  models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "ResultsConsulidatioPermission " 
    
class SubVideoTask(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_number = models.IntegerField(blank=False, null=False) 
    task_name = models.CharField(max_length=99999,default="x")

    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    screen_sub_video_emotions=models.FileField(upload_to="videos/", default=None)
    screen_sub_video_sem_emotions=models.FileField(upload_to="videos/", default=None)
    actions = models.CharField(max_length=99999,default="x")
    emotions_plot_info = models.CharField(max_length=99999,default="x")

    #Usability Smells
    usabilitySmells = models.CharField(max_length=99999,default="uS")


    def __str__(self):
        return str(self.video.usability_test_name)

class UsabilityEval_CW_Smells_Emotion(models.Model):
    subVideoTask = models.ForeignKey(SubVideoTask, on_delete=models.CASCADE,default=None)
    teamMember = models.ForeignKey(TeamMember, on_delete=models.CASCADE,default=None)

    #CW
    eval_done_with_emotion =  models.BooleanField(default=False)  
    q1_with_emotion = models.CharField(max_length=99999,default="x")
    q2_with_emotion = models.CharField(max_length=99999,default="x")
    q3_with_emotion = models.CharField(max_length=99999,default="x")
    q4_with_emotion = models.CharField(max_length=99999,default="x")
    notes_with_emotion = models.CharField(max_length=99999,default="x")

    #Smells
    usabilitySmells_selected_with_emotion = models.CharField(max_length=99999,default="[]")
    usabilitySmells_done_with_emotion =  models.BooleanField(default=False)  
    usabilitySmells_notes_with_emotion =  models.CharField(max_length=99999,default="x")


    def __str__(self):
        return "teamMember: " + str(self.teamMember.user.username) +  " ->  UsabilityEval_CW_Smells_Emotion" 


class UsabilityEval_CW_Smells_without_Emotion(models.Model):
    subVideoTask = models.ForeignKey(SubVideoTask, on_delete=models.CASCADE,default=None)
    teamMember = models.ForeignKey(TeamMember, on_delete=models.CASCADE,default=None)   

    #CW
    eval_done_without_emotion =  models.BooleanField(default=False)  
    q1_without_emotion = models.CharField(max_length=99999,default="x")
    q2_without_emotion = models.CharField(max_length=99999,default="x")
    q3_without_emotion = models.CharField(max_length=99999,default="x")
    q4_without_emotion = models.CharField(max_length=99999,default="x")
    notes_without_emotion = models.CharField(max_length=99999,default="x")
    
    #Smells
    usabilitySmells_selected_without_emotion = models.CharField(max_length=99999,default="[]")
    usabilitySmells_done_without_emotion =  models.BooleanField(default=False)  
    usabilitySmells_notes_without_emotion =  models.CharField(max_length=99999,default="x") 
    
    def __str__(self):
        return "teamMember: " + str(self.teamMember.user.username) +  " ->  UsabilityEval_CW_Smells_without_Emotion" 

class ResultsConsulidation(models.Model):
    subVideoTask = models.ForeignKey(SubVideoTask, on_delete=models.CASCADE,default=None)
    #CW
    eval_done_with_emotion =  models.BooleanField(default=False)  
    q1_with_emotion = models.CharField(max_length=99999,default="x")
    q2_with_emotion = models.CharField(max_length=99999,default="x")
    q3_with_emotion = models.CharField(max_length=99999,default="x")
    q4_with_emotion = models.CharField(max_length=99999,default="x")
    notes_with_emotion = models.CharField(max_length=99999,default="x")
    number_usability_problems_CW_with_emotion = models.IntegerField( blank=True, null=True) 

    #Smells
    usabilitySmells_selected_with_emotion = models.CharField(max_length=99999,default="[]")
    usabilitySmells_done_with_emotion =  models.BooleanField(default=False)  
    usabilitySmells_notes_with_emotion =  models.CharField(max_length=99999,default="x")
    number_usability_problems_Smells_with_emotion = models.IntegerField( blank=True, null=True) 

    #without emotions--------------
    #CW
    eval_done_without_emotion =  models.BooleanField(default=False)  
    q1_without_emotion = models.CharField(max_length=99999,default="x")
    q2_without_emotion = models.CharField(max_length=99999,default="x")
    q3_without_emotion = models.CharField(max_length=99999,default="x")
    q4_without_emotion = models.CharField(max_length=99999,default="x")
    notes_without_emotion = models.CharField(max_length=99999,default="x")
    number_usability_problems_CW_without_emotion = models.IntegerField( blank=True, null=True) 

    #Smells
    usabilitySmells_selected_without_emotion = models.CharField(max_length=99999,default="[]")
    usabilitySmells_done_without_emotion =  models.BooleanField(default=False)  
    usabilitySmells_notes_without_emotion =  models.CharField(max_length=99999,default="x")    
    number_usability_problems_Smells_without_emotion = models.IntegerField( blank=True, null=True) 

    def __str__(self):
        return "ResultsConsulidation "