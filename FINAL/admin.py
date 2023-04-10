from django.contrib import admin
from .models import Video
from .models import *

# Register your models here.
admin.site.register(TeamLeader)
admin.site.register(TeamMember)
admin.site.register(Project)

admin.site.register(SubVideoTask)
admin.site.register(Video)
admin.site.register(Invitations)
admin.site.register(UsabilityEval_CW_Smells_Emotion )
admin.site.register(UsabilityEval_CW_Smells_without_Emotion )

