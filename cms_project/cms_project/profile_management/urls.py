from django.urls import path
from profile_management.views.profile import profile_list, profile_detail

app_name = 'profile_management'

urlpatterns = [
    path('', profile_list, name='profile_list'),  # List all profiles
    path('<int:id>/', profile_detail, name='profile_detail'),  # View a specific profile
]
