from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import InventoryItem, Item, PlayerProfile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import random
import json  
from .models import PlayerProfile, Encounter, InventoryItem
from django.shortcuts import render
from django.shortcuts import redirect


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
@login_required
def perform_attack(request):
    if request.method == "POST":
        player = request.user.playerprofile
        
        try:
            data = json.loads(request.body)
            action_type = data.get("action_type", "fight") 
        except json.JSONDecodeError:
            action_type = "fight"
        
        active_encounter = player.encounters.filter(status="ACTIVE").first()
        
        if not active_encounter:
            return JsonResponse({"error": "No active enemies around you!"}, status=400)

        enemy_type = active_encounter.enemy_type
        
        if action_type == "magic":
            player_damage = random.randint(25, 40)
            log_message = f"🔥 You cast a blazing FIREBALL at the {enemy_type.name} for {player_damage} damage! "
        elif action_type == "fight":
            player_damage = random.randint(10, 20)
            log_message = f"⚔️ You bravely slashed the {enemy_type.name} for {player_damage} damage! "
        else:
            player_damage = 0
            log_message = f"You did something unknown... "

        enemy_damage = enemy_type.damage

        active_encounter.enemy_hp -= player_damage

        game_status = "ongoing"

        if active_encounter.enemy_hp <= 0:
            
            # Zombie revive
            if enemy_type.name == "ZOMBIE" and enemy_type.can_revive:
                active_encounter.enemy_hp = enemy_type.max_hp // 2 
                enemy_type.can_revive = False 
                log_message += f"<br><br>🧟‍♂️ Oh no! The Zombie reanimates from the dead!"
                game_status = "ongoing"
                
            else:
                active_encounter.enemy_hp = 0
                active_encounter.status = "WON" 
            
                # Rewards
                player.monsters_defeated += 1
                player.coins += enemy_type.reward_coins
            
                log_message += f"<br><br>✨ Victory! The {enemy_type.name} has been defeated! You earned {enemy_type.reward_coins} coins."
                game_status = "won"
            
                # Dropped item determination
                if enemy_type.drops_item:
                    inv_item, created = InventoryItem.objects.get_or_create(
                        player=player, 
                        item=enemy_type.drops_item,
                        defaults={'quantity': 0}
                    )
                    inv_item.quantity += 1
                    inv_item.save()
                    log_message += f"<br>🎁 Loot! You found a {enemy_type.drops_item.name} and put it in your inventory!"

        else:
            player.hp -= enemy_damage
            log_message += f"<br>The {enemy_type.name} hit you back for {enemy_damage} damage."
            
            if player.hp <= 0:
                player.hp = 0
                active_encounter.status = "LOST"
                log_message += f"<br><br>☠️ You have been slain by the {enemy_type.name}..."
                game_status = "lost"

        #Save
        active_encounter.save()
        player.save()

        enemy_hp_percent = 0
        if enemy_type.max_hp > 0:
            enemy_hp_percent = int((active_encounter.enemy_hp / enemy_type.max_hp) * 100)

        return JsonResponse({
            "player_hp": player.hp,
            "enemy_hp_percent": enemy_hp_percent,
            "log_message": log_message,
            "game_status": game_status
        })
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def restart_game(request):
    player = request.user.playerprofile
    
    player.hp = 100  
    
    player.coins = int(player.coins * 0.8) 
    player.save()
    
   
    player.encounters.filter(status__in=["ACTIVE", "LOST"]).delete()
    
    
    return redirect('game:main')
