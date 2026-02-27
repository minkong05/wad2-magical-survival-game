from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

from .forms import UserForm, UserProfileForm

def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect("home") 
            else:
                return render(request, "accounts/login.html", {
                    "error": "Your account is disabled."
                })
        else:

            return render(request, "accounts/login.html", {
                "error": "Invalid username or password."
            })

    else:
        return render(request, "accounts/login.html")
    

def user_register(request):
    registered = False

    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()


            profile = profile_form.save(commit=False)
            profile.user = user

            if "picture" in request.FILES:
                profile.picture = request.FILES["picture"]

            profile.save()

            registered = True
            return redirect("home") 
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, "accounts/register.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "registered": registered,
        },
    )


def user_logout(request):
    logout(request)
    return redirect("home") 