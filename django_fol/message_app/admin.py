from django.contrib import admin

# Register your models here.

from .models import Post,Question,Choice
admin.site.register(Post)
admin.site.register(Question)
admin.site.register(Choice)