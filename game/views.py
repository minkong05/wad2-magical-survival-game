from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import PlayerProfile

# Create your views here.

def main(request):
    return render(request,'core/main.html')


@login_required
def character_select(request):
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        class_type = request.POST.get("class_type")

        if class_type in dict(PlayerProfile.CLASS_CHOICES):
            profile.class_type = class_type
            profile.save()
            return redirect("core:main")

    return render(request, "game/character_select.html", {
        "choices": PlayerProfile.CLASS_CHOICES,
        "current": profile.class_type,
    })