"""LITReview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from critique.views import (
    ReviewDeleteView,
    TicketDeleteView,
    create_ticket,
    ticket_update,
    create_review,
    flux,
    posts,
    review_response,
    ticket_detail,
    review_detail,
    review_update,
)
from authentification.views import (
    logout_user,
    profile,
    signup_page,
    login_page,
    subscriptions,
    UnsubscribeView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    # authentification

    path("", login_page, name="login"),
    path("signup/", signup_page, name="signup"),
    path("logout/", logout_user, name="logout"),
    path("profile/", profile, name="profile"),
    path("subscriptions/", subscriptions, name="subscriptions"),
    path("unsubscribe/<int:pk>/", UnsubscribeView.as_view(), name="unsubscribe"),

    # critique
    
    path("flux/", flux, name="flux"),
    path("posts/", posts, name="posts"),
    path("user-posts/<int:pk>/", posts, name="user_posts"),
    path("create-ticket/", create_ticket, name="create_ticket"),
    path("ticket/<int:pk>/update/", ticket_update, name="ticket_update"),
    path("ticket/<int:pk>/detail", ticket_detail, name="ticket_detail"),
    path("ticket/<int:pk>/delete/", TicketDeleteView.as_view(), name="ticket_delete"),
    path("create-review/", create_review, name="create_review"),
    path("review/<int:pk>/detail", review_detail, name="review_detail"),
    path("review-response/<int:pk>", review_response, name="response_review"),
    path("review/<int:pk>/update/", review_update, name="review_update"),
    path("review/<int:pk>/delete/", ReviewDeleteView.as_view(), name="review_delete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
