from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, "core/home.html")

def aboutus(request):
    return render(request, "core/aboutus.html")

@login_required
def main(request):
    return render(request, "core/main.html")
