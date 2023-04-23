
from django.contrib import admin
from app import views
from django.urls import path,include,reverse
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),    
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('account/', views.account, name='account'),
    

    #TEAM LEADER ----------------------------------------------------------------------------------
    path('resultsConsolidation_permissions/', views.resultsConsolidation_permissions, name='resultsConsolidation_permissions'),
    path('resultsConsolidation_usabilityTests_permissions/<int:projectID>', views.resultsConsolidation_usabilityTests_permissions, name='resultsConsolidation_usabilityTests_permissions'),
    path('allow_TM_resultsConsolidation/<int:videoID>', views.allow_TM_resultsConsolidation, name='allow_TM_resultsConsolidation'),
    path('not_allow_TM_resultsConsolidation/<int:videoID>', views.not_allow_TM_resultsConsolidation, name='not_allow_TM_resultsConsolidation'),

    path('results/', views.results, name='results'),
    path('projectResults/<int:projectID>', views.projectResults, name='projectResults'),

    path('resultsConsolidation/', views.resultsConsolidation, name='resultsConsolidation'),
    path('resultsConsolidation_usabilityTests/<int:projectID>', views.resultsConsolidation_usabilityTests, name='resultsConsolidation_usabilityTests'),
    path('resultsConsolidation_TM_evaluation/<str:evalType>/<int:videoID>', views.resultsConsolidation_TM_evaluation, name='resultsConsolidation_TM_evaluation'),

    path('manage_Invitations/', views.manage_Invitations, name='manage_Invitations'),
    path('create_Invitations/', views.create_Invitations, name='create_Invitations'),
    path('deleteInvitation/<int:id>', views.deleteInvitation, name='deleteInvitation'),

    path('manage_projects/', views.manage_projects, name='manage_projects'),
    path('create_project/', views.create_project, name='create_project'),
    path('deleteProject/<int:id>', views.deleteProject, name='deleteProject'),
    path('editProject/<int:id>', views.editProject, name='editProject'),
    
    path('usabilityTestUpload/', views.usabilityTestUpload, name='usabilityTestUpload'),
    path('selectedVideoToSplit/<int:id>', views.selectedVideoToSplit, name='selectedVideoToSplit'),
    path('selectVideoToSplit/', views.selectVideoToSplit, name='selectVideoToSplit'),
    
    path('splitVideo/', views.splitVideo, name='splitVideo'),
    path('videoSplitSubvideos/', views.videoSplitSubvideos, name='videoSplitSubvideos'),

    path('manageTestingVideos/', views.manageTestingVideos, name='manageTestingVideos'),
    path('deleteVideo/<int:id>', views.deleteVideo, name='deleteVideo'),
    path('updateVideo/<int:id>', views.updateVideo, name='updateVideo'),
    path('editUserTasks/<int:id>', views.editUserTasks, name='editUserTasks'),
    path('deleteTask/<int:id>/<int:idVideo>', views.deleteTask, name='deleteTask'),

    path('CW_editUserTask/<int:id>', views.CW_editUserTask, name='CW_editUserTask'),
    path('Smells_editUserTask/<int:id>', views.Smells_editUserTask, name='Smells_editUserTask'),
    #END TEAM LEADER -------------------------------------------------------------------------------


    #TEAM MEMBER -----------------------------------------------------------------------------------
    path('manage_usabilitySmells/', views.manage_usabilitySmells, name='manage_usabilitySmells'),
    path('create_usabilitySmell/', views.create_usabilitySmell, name='create_usabilitySmell'),
    path('editUsabilitySmells/<int:id>', views.editUsabilitySmells, name='editUsabilitySmells'),
    path('deleteUsabilitySmell/<int:id>', views.deleteUsabilitySmell, name='deleteUsabilitySmell'),

    path('manage_heuristicEvaluations/', views.manage_heuristicEvaluations, name='manage_heuristicEvaluations'),
    path('create_heuristicEvaluation/', views.create_heuristicEvaluation, name='create_heuristicEvaluation'),
    path('editHeuristicEvaluation/<int:id>', views.editHeuristicEvaluation, name='editHeuristicEvaluation'),
    path('deleteHeuristicEvaluation/<int:id>', views.deleteHeuristicEvaluation, name='deleteHeuristicEvaluation'),

    path('manage_teamMember_Invitations/', views.manage_teamMember_Invitations, name='manage_teamMember_Invitations'),
    path('accept_teamMember_Invitation/<int:id>', views.accept_teamMember_Invitation, name='accept_teamMember_Invitation'),

    path('CW_usability_tests_resultsConsolidation/<int:id>', views.CW_usability_tests_resultsConsolidation, name='CW_usability_tests_resultsConsolidation'),
    path('CW_tasks_resultsConsolidation/<str:x>/<str:projName>/<int:projID>/<int:id>', views.CW_tasks_resultsConsolidation, name='CW_tasks_resultsConsolidation'),
    path('CW_evaluateTask_resultsConsolidation/<str:x>/<str:projName>/<int:projID>/<int:id>', views.CW_evaluateTask_resultsConsolidation, name='CW_evaluateTask_resultsConsolidation'),

    path('CW_usability_tests/<int:id>', views.CW_usability_tests, name='CW_usability_tests'),
    path('CW_tasks/<str:x>/<str:projName>/<int:projID>/<int:id>', views.CW_tasks, name='CW_tasks'),
    path('CW_evaluateTask/<str:x>/<str:projName>/<int:projID>/<int:id>', views.CW_evaluateTask, name='CW_evaluateTask'),
    
    path('Smells_usability_tests_resultsConsolidation/<int:id>', views.Smells_usability_tests_resultsConsolidation, name='Smells_usability_tests_resultsConsolidation'),
    path('Smells_tasks_resultsConsolidation/<str:x>/<str:projName>/<int:projID>/<int:id>', views.Smells_tasks_resultsConsolidation, name='Smells_tasks_resultsConsolidation'),
    path('Smells_evaluateTask_resultsConsolidation/<str:x>/<str:projName>/<int:projID>/<int:id>', views.Smells_evaluateTask_resultsConsolidation, name='Smells_evaluateTask_resultsConsolidation'),

    path('Smells_usability_tests/<int:id>', views.Smells_usability_tests, name='Smells_usability_tests'),
    path('Smells_tasks/<str:x>/<str:projName>/<int:projID>/<int:id>', views.Smells_tasks, name='Smells_tasks'),
    path('Smells_evaluateTask/<str:x>/<str:projName>/<int:projID>/<int:id>', views.Smells_evaluateTask, name='Smells_evaluateTask'),
    #END TEAM MEMBER --------------------------------------------------------------------------------



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
