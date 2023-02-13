from django.contrib import admin

from .models import Profile, UserFollow

admin.site.register([Profile, UserFollow])
