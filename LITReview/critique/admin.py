from django.contrib import admin

from .models import Ticket, Review

admin.site.register([Ticket, Review])