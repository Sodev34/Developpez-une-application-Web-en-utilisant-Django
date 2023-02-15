from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import (
    ImageUpdateForm,
    ProfileUpdateForm,
    SignupForm,
    LoginForm,
    SubscribeForm,
)
from .models import UserFollow


def login_page(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("flux")
            else:
                messages.error(request, f"Identifiant ou mot de passe incorrect")
    else:
        form = LoginForm()

    return render(request, "authentification/login.html", {"form": form})


def signup_page(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = SignupForm()

    return render(request, "authentification/signup.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        p_form = ProfileUpdateForm(request.POST, instance=request.user)
        i_form = ImageUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if p_form.is_valid() and i_form.is_valid():
            p_form.save()
            i_form.save()
            return redirect("profile")

    else:
        p_form = ProfileUpdateForm(instance=request.user)
        i_form = ImageUpdateForm(instance=request.user.profile)

    context = {
        "p_form": p_form,
        "i_form": i_form,
    }

    return render(request, "authentification/profile.html", context)


def logout_user(request):
    logout(request)
    return redirect("login")


@login_required
def subscriptions(request):
    if request.method == "POST":
        form = SubscribeForm(request.POST)

        if form.is_valid():
            try:
                followed_user = User.objects.get(username=request.POST["followed_user"])
                if request.user == followed_user:
                    messages.error(
                        request, "Vous ne pouvez pas vous abonner à votre compte !"
                    )
                else:
                    try:
                        UserFollow.objects.create(
                            user=request.user, followed_user=followed_user
                        )
                        messages.success(
                            request, f"Vous suivez maintenant {followed_user} !"
                        )
                    except IntegrityError:
                        messages.error(request, f"Vous suivez déjà {followed_user} !")

            except User.DoesNotExist:
                messages.error(request, f"Cette utilisateur est introuvable !")

    else:
        form = SubscribeForm()

    user_follows = UserFollow.objects.filter(user=request.user).order_by(
        "followed_user"
    )
    followed_by = UserFollow.objects.filter(followed_user=request.user).order_by("user")

    context = {
        "form": form,
        "user_follows": user_follows,
        "followed_by": followed_by,
        "title": "Subscriptions",
    }

    return render(request, "authentification/subscriptions.html", context)


class UnsubscribeView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = UserFollow
    success_url = "/subscriptions"
    context_object_name = "unsub"

    def test_func(self):
        unsub = self.get_object()
        if self.request.user == unsub.user:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        return super(UnsubscribeView, self).delete(request, *args, **kwargs)
