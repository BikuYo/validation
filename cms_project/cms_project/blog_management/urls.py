from django.urls import path
from blog_management.views.blog import blog_list, blog_detail,theme
from blog_management.views.comment import add_comment

app_name = 'blog_management'

urlpatterns = [
    path('', theme, name='theme'),  # List all blogs
    path('blog_list', blog_list, name='blog_list'),  # List all blogs
    path('<int:id>/', blog_detail, name='blog_detail'),  # View details of a single blog
    path('<int:blog_id>/add_comment/', add_comment, name='add_comment'),  # Add a comment to a blog
]
