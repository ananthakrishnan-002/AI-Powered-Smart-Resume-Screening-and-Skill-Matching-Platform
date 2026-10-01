from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from resumes.views import (
    home,
    candidate_dashboard,
    recruiter_dashboard,
    upload_resume,
)

urlpatterns = [
    path('', home, name='home'),

    path('users/', include('users.urls')),
    path('jobs/', include('jobs.urls')),


    path('admin/', admin.site.urls),

    path(
        'candidate/dashboard/',
        candidate_dashboard,
        name='candidate_dashboard'
    ),

    path(
        'candidate/upload/',
        upload_resume,
        name='upload_resume'
    ),

    path(
        'recruiter/dashboard/',
        recruiter_dashboard,
        name='recruiter_dashboard'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )