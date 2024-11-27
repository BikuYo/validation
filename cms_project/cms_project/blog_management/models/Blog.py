from django.db import models
from tag_management.models.Tag import Tag

class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name="blogs")

    def __str__(self):
        return self.title
