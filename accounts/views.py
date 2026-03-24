from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .forms import UserForm, UserProfileForm
from .models import UserProfile
from game.models import PlayerProfile

def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                profile, _ = PlayerProfile.objects.get_or_create(user=user)
                if not profile.class_selected:
                    return redirect("game:character_select")
                return redirect("core:main")
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
    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            
            if 'password' in user_form.cleaned_data:
                user.set_password(user_form.cleaned_data['password'])
            
            user.save() 
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            return redirect("core:home") 
        else:
            print("User errors:", user_form.errors)
            print("Profile errors:", profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, "accounts/register.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })

@login_required
def myaccount(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    player_profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    profile_form = UserProfileForm(instance=user_profile)
    upload_status = request.GET.get("updated") == "1"

    if request.method == "POST":
        upload_status = False
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if not request.FILES.get("picture"):
            profile_form.add_error("picture", "Please choose an image file to upload.")

        if profile_form.is_valid():
            profile_form.save()
            return redirect(f"{reverse('core:myaccount')}?updated=1")

    learned_skills = list(
        player_profile.friends
        .select_related("friend")
        .order_by("-unlocked_at")
        .values_list("friend__name", flat=True)[:3]
    )

    active_companion = (
        player_profile.friends
        .select_related("friend")
        .filter(is_active=True)
        .first()
    )
    inventory_totals = player_profile.inventory.aggregate(total_quantity=Sum("quantity"))
    total_inventory_items = inventory_totals["total_quantity"] or 0
    unique_inventory_items = player_profile.inventory.filter(quantity__gt=0).count()

    return render(
        request,
        "accounts/myaccount.html",
        {
            "user_profile": user_profile,
            "player_profile": player_profile,
            "learned_skills": learned_skills,
            "active_companion_name": active_companion.friend.name if active_companion else "None",
            "total_inventory_items": total_inventory_items,
            "unique_inventory_items": unique_inventory_items,
            "profile_form": profile_form,
            "upload_status": upload_status,
        },
    )


def user_logout(request):
    logout(request)
    return redirect("core:home") 
