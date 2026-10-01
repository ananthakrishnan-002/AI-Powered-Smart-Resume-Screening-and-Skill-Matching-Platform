from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required



def register(request):

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')

    else:
        form = UserRegisterForm()

    return render(
        request,
        'registration/register.html',
        {
            'form': form
        }
    )


def user_login(request):

    if request.method == 'POST':
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.role == 'candidate':
                return redirect(
                    'candidate_dashboard'
                )
            else:
                return redirect(
                    'recruiter_dashboard'
                )

    else:
        form = AuthenticationForm()

    return render(
        request,
        'registration/login.html',
        {
            'form': form
        }
    )


def user_logout(request):
    logout(request)
    return redirect('home')

from django.contrib import messages
from .models import CandidateProfile, RecruiterProfile
from .forms import CandidateProfileForm, RecruiterProfileForm

@login_required
def profile_view(request):
    user = request.user
    if user.role == 'candidate':
        profile, created = CandidateProfile.objects.get_or_create(user=user)
        if request.method == 'POST':
            form = CandidateProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('candidate_dashboard')
        else:
            form = CandidateProfileForm(instance=profile)
    else:
        profile, created = RecruiterProfile.objects.get_or_create(user=user)
        if request.method == 'POST':
            form = RecruiterProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('recruiter_dashboard')
        else:
            form = RecruiterProfileForm(instance=profile)
            
    return render(request, 'profile.html', {'form': form, 'profile': profile})