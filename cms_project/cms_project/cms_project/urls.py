"""
URL configuration for cms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from validation_app.views import execute_sql_query, validation_type,mapping,result, \
execute_sql_with_join_type,sql_validation_view,sparkdataProcessing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blogs/', include('blog_management.urls')),
    path('profiles/', include('profile_management.urls')),
    path('tags/', include('tag_management.urls')),
    path('sql-query/', execute_sql_query, name='sql_query'),
    path('execute_sql_with_join_type/', execute_sql_with_join_type, name='execute_sql_with_join_type'),
    path('validation_type/', validation_type, name='validation_type'),
    path('mapping/', mapping, name='mapping'),
    path('result/', result, name='result'),
    path('sql_validation_view/', sql_validation_view, name='sql_validation_view'),
    path('sparkdataProcessing/', sparkdataProcessing, name='sparkdataProcessing'),
]
