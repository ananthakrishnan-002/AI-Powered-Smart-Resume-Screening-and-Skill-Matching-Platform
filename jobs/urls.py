from django.urls import path
from .views import (
    job_list,
    create_job,
    edit_job,
    delete_job,
    job_detail,
    apply_job,
    applied_jobs,
    shortlist_candidate,
    reject_candidate,
    applicant_detail,
    export_applicants_csv,
)

urlpatterns = [
    path('', job_list, name='job_list'),
    path('create/', create_job, name='create_job'),
    path('<int:job_id>/edit/', edit_job, name='edit_job'),
    path('<int:job_id>/delete/', delete_job, name='delete_job'),
    path('<int:job_id>/', job_detail, name='job_detail'),
    path('<int:job_id>/apply/', apply_job, name='apply_job'),
    path('applied/', applied_jobs, name='applied_jobs'),
    path('shortlist/<int:app_id>/', shortlist_candidate, name='shortlist_candidate'),
    path('reject/<int:app_id>/', reject_candidate, name='reject_candidate'),
    path('applicant/<int:app_id>/', applicant_detail, name='applicant_detail'),
    path('<int:job_id>/export/', export_applicants_csv, name='export_applicants_csv'),
]
