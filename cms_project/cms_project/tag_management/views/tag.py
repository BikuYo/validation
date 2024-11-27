from django.shortcuts import render
from tag_management.models.Tag import Tag

def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'tag_management/tag_list.html', {'tags': tags})
