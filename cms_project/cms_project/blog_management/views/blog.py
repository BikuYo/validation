from django.shortcuts import render, get_object_or_404
from blog_management.models.Blog import Blog

def theme(request):
    blogs = Blog.objects.all()
    return render(request, 'adminlte/base.html')

def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, 'blog_management/blog_list.html', {'blogs': blogs})

def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    return render(request, 'blog_management/blog_detail.html', {'blog': blog})
