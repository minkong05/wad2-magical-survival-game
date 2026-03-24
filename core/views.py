from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, "core/home.html")

def aboutus(request):
    return render(request, "core/aboutus.html")

@login_required
def main(request):
    return redirect("game:main")
