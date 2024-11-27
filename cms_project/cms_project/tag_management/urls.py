from django.urls import path
from tag_management.views.tag import tag_list

app_name = 'tag_management'

urlpatterns = [
    path('', tag_list, name='tag_list'),  # List all tags
]
