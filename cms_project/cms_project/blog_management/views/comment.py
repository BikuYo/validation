from django.shortcuts import redirect
from blog_management.models.Comment import Comment
from blog_management.models.Blog import Blog

def add_comment(request, blog_id):
    if request.method == 'POST':
        blog = Blog.objects.get(id=blog_id)
        content = request.POST.get('content')
        Comment.objects.create(blog=blog, author='Anonymous', content=content)
    return redirect('blog_management:blog_detail', id=blog_id)
