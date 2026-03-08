from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import InventoryItem, Item, PlayerProfile

def main(request):
    return render(request,'core/main.html')


@login_required
def shop(request):

    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

    items = Item.objects.all().order_by("price", "name")

    context = {
        "profile": profile,
        "items": items,
    }
    return render(request, "game/shop.html", context)


@login_required
def buy_item(request, item_id):
    if request.method != "POST":
        return redirect("game:shop")

    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    item = get_object_or_404(Item, id=item_id)

    if profile.coins < item.price:
        messages.error(request, "Not enough coins.")
        return redirect("game:shop")

    profile.coins -= item.price
    profile.save()

    inv, created = InventoryItem.objects.get_or_create(
        player=profile,
        item=item,
        defaults={"quantity": 0},
    )
    inv.quantity += 1
    inv.save()

    messages.success(request, f"Bought {item.name}!")
    return redirect("game:shop")