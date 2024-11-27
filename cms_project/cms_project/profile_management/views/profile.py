from django.shortcuts import render, get_object_or_404
from profile_management.models.Profile import Profile

def profile_list(request):
    profiles = Profile.objects.all()
    return render(request, 'profile_management/profile_list.html', {'profiles': profiles})

def profile_detail(request, id):
    profile = get_object_or_404(Profile, id=id)
    return render(request, 'profile_management/profile_detail.html', {'profile': profile})
