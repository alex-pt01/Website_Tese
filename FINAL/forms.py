from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from app.models import  *

from django.contrib.auth.models import AbstractUser



class InvitationForm(forms.Form):
    projectID = forms.IntegerField(label='Project', required=False) #projectID
    teamMemberEmail = forms.EmailField(max_length = 200)
    class Meta:
        model = Invitations
        fields = ['projectID', 'teamMemberEmail']
        
class SelectVideoForm(forms.ModelForm):
    video = forms.ModelChoiceField(queryset=Video.objects.all(), required=True)
    class Meta:
        model = Video
        fields = ['video']
        
class newUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    teamLeader = forms.BooleanField(label='Team Leader', required=False, widget=forms.CheckboxInput(attrs={
   
    'class': 'switch',
    'data-on': 'Enabled',
    'data-off': 'Disabled'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2','teamLeader']

class updateUserForm(forms.Form):
    first_name = forms.CharField(label='First Name', required=False, error_messages={
               'required': 'Please enter your first name'
                })
    last_name = forms.CharField(label='Last Name', required=False, error_messages={
               'required': 'Please enter your last name'
                })
    username = forms.CharField(label='Username', required=False, error_messages={
               'required': 'Please enter your username'
                })
    email = forms.EmailField(label='Your Email', required=False, error_messages={
               'required': 'Please enter your email'
                })
    currentPassword = forms.CharField(label='Current Password', widget=forms.PasswordInput(), required=True, error_messages={
               'required': 'Please enter your current password'
                })

class DateTimePickerInput(forms.DateTimeInput):
        input_type = 'datetime'

class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"
 
class DateTimeLocalField(forms.DateTimeField):
    input_formats = [
        "%Y-%m-%dT%H:%M:%S", 
        "%Y-%m-%dT%H:%M:%S.%f", 
        "%Y-%m-%dT%H:%M"
    ]
    widget = DateTimeLocalInput(format="%Y-%m-%dT%H:%M")
    
class ProjectForm(forms.ModelForm):
    name = forms.CharField(label='Name', required=True)
    description = forms.CharField(label='Description', required=True)
    start_date = DateTimeLocalField()
    end_date = DateTimeLocalField()

    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 
                  'end_date']

class UsabilitySmellsForm(forms.ModelForm):
    usabilitySmell = forms.CharField(label='Usability Smell', required=False)
    description = forms.CharField(label='Description', required=False)
    class Meta:
        model = UsabilitySmells
        fields = ['usabilitySmell', 'description']

class HeuristicEvaluationForm(forms.ModelForm):
    heuristicName = forms.CharField(label='Heuristic Name', required=False)
    description = forms.CharField(label='Description', required=False)
    class Meta:
        model = HeuristicEvaluation
        fields = ['heuristicName', 'description']

class ProjectSearchForm(forms.ModelForm):
    name = forms.CharField(label='Name', required=False)
    description = forms.CharField(label='Description', required=False)
    start_date = DateTimeLocalField( required=False)
    end_date = DateTimeLocalField( required=False)

    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 
                  'end_date']
        
class InvitationSearchForm(forms.Form):
    proj_name = forms.CharField(label='Project Name', required=False)
    member_name = forms.CharField(label='Team Member Name', required=False)
    teamMemberEmail = forms.EmailField(max_length = 200,required=False)
    start_date = DateTimeLocalField( required=False)
    end_date = DateTimeLocalField( required=False)
    created_at = DateTimeLocalField( required=False)
    class Meta:
        fields = ('proj_name', 'member_name', 'teamMemberEmail','start_date', 'end_date', 'created_at')

class InvitationTMSearchForm(forms.Form):
    proj_name = forms.CharField(label='Project Name', required=False)
    leader_name = forms.CharField(label='Team Leader Name', required=False)
    teamLeaderEmail = forms.EmailField(max_length = 200,required=False)
    start_date = DateTimeLocalField( required=False)
    end_date = DateTimeLocalField( required=False)
    class Meta:
        fields = ('proj_name', 'leader_name', 'teamLeaderEmail','start_date', 'end_date')

                     

class VideoForm(forms.ModelForm):
    project = forms.CharField(label='Project', required=True)
    usability_test_name = forms.CharField(label='Usability test name', required=True)
    user_type = forms.CharField(label='User Type', required=True)
    user_UID = forms.IntegerField(label='User UID', required=True)
    local = forms.CharField(label='Local', required=True)

    class Meta:
        model = Video
        fields = ['usability_test_name', 'user_type', 'user_UID', 
                  'local', 'webcam_video', 
                    'screen_video']

class VideoEditForm(forms.ModelForm):
    usability_test_name = forms.CharField(label='Usability test name', required=False)
    user_type = forms.CharField(label='User Type', required=False)
    user_UID = forms.IntegerField(label='User UID', required=False)
    local = forms.CharField(label='Local', required=False)

    class Meta:
        model = Video
        fields = ['usability_test_name', 'user_type', 'user_UID', 
                  'local']


class selectVideoSearchForm(forms.Form):
    proj_name = forms.CharField(label='Project name', required=False)
    usability_test_name = forms.CharField(label='Usability test name', required=False)
    user_type = forms.CharField(label='User type', required=False)
    user_UID = forms.IntegerField(label='User UID', required=False)
    local = forms.CharField(label='Local', required=False)
    splited_bool  = forms.ChoiceField(choices = (
    ("Yes", "Yes"),
    ("No", "No")),required=False)

    class Meta:
        #model = Project
        fields = ('proj_name', 'usability_test_name', 'user_type','user_UID', 'local', 'splited_bool')



class EditSubVideoTaskForm(forms.ModelForm):
    task_number = forms.CharField(label='Task number', required=False)
    actions = forms.CharField(label='Actions', required=False)
    usabilitySmells = forms.CharField(label='Usability Smells', required=False)

    class Meta:
        model = SubVideoTask
        fields = ['task_number', 'actions', 'usabilitySmells']

class TaskWithEmotionForm(forms.ModelForm):
    q1_with_emotion = forms.CharField(label='CW Question 1', required=False)
    q2_with_emotion = forms.CharField(label='CW Question 2', required=False)
    q3_with_emotion = forms.CharField(label='CW Question 3', required=False)
    q4_with_emotion = forms.CharField(label='CW Question 4', required=False)
    notes_with_emotion = forms.CharField(label='Notes', required=False)
    eval_done_with_emotion = forms.BooleanField(label='Done', required=False, widget=forms.CheckboxInput(attrs={

    'class': 'switch',
    'data-on': 'Enabled',
    'data-off': 'Disabled'}))
    number_usability_problems_CW_with_emotion = forms.CharField(label='Number of Usability Problems', required=False)



    usabilitySmells_notes_with_emotion = forms.CharField(label='Notes', required=False)
    usabilitySmells_done_with_emotion = forms.BooleanField(label='Done', required=False)
    number_usability_problems_Smells_with_emotion = forms.CharField(label='Number of Usability Problems', required=False)

    class Meta:
        model = SubVideoTask
        fields = [ 'q1_with_emotion', 'q2_with_emotion', 
                  'q3_with_emotion', 'q4_with_emotion', 
                    'notes_with_emotion','eval_done_with_emotion', 
                    'usabilitySmells_notes_with_emotion', 'usabilitySmells_done_with_emotion',
                    'number_usability_problems_CW_with_emotion', 'number_usability_problems_Smells_with_emotion']

class TaskWithoutEmotionForm(forms.ModelForm):
    q1_without_emotion = forms.CharField(label='CW Question 1', required=False)
    q2_without_emotion = forms.CharField(label='CW Question 2', required=False)
    q3_without_emotion = forms.CharField(label='CW Question 3', required=False)
    q4_without_emotion = forms.CharField(label='CW Question 4', required=False)
    notes_without_emotion = forms.CharField(label='Notes', required=False)
    eval_done_without_emotion = forms.BooleanField(label='Done', required=False,widget=forms.CheckboxInput(attrs={
    'class': 'switch',
    'data-on': 'Enabled',
    'data-off': 'Disabled'}))
    number_usability_problems_CW_without_emotion = forms.CharField(label='Number of Usability Problems', required=False)

    usabilitySmells_notes_without_emotion = forms.CharField(label='Notes', required=False)
    usabilitySmells_done_without_emotion = forms.BooleanField(label='Done', required=False)
    number_usability_problems_Smells_without_emotion = forms.CharField(label='Number of Usability Problems', required=False)

    class Meta:
        model = SubVideoTask
        fields = [ 'q1_without_emotion', 'q2_without_emotion', 
                  'q3_without_emotion', 'q4_without_emotion', 
                    'notes_without_emotion','eval_done_without_emotion',
                    'usabilitySmells_notes_without_emotion','usabilitySmells_done_without_emotion',
                    'number_usability_problems_CW_without_emotion', 'number_usability_problems_Smells_without_emotion' ]

