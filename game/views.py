from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import InventoryItem, Item, PlayerProfile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import random
import json  
from .models import PlayerProfile, Encounter, InventoryItem, EnemyType, FriendType
from django.shortcuts import render
from django.shortcuts import redirect


@login_required
def main(request):
    player = request.user.playerprofile
    
    active_encounter = player.encounters.filter(status="ACTIVE").first()

    if not active_encounter:
        if player.monsters_defeated == 0:
            enemy = EnemyType.objects.filter(name="SKULL").first()
        elif player.monsters_defeated == 1:
            enemy = EnemyType.objects.filter(name="ZOMBIE").first()
        elif player.monsters_defeated == 2:
            enemy = EnemyType.objects.filter(name="WITCH").first()
        else:
            enemy = EnemyType.objects.filter(name="DRAGON").first()
            
        if not enemy:
            enemy = EnemyType.objects.first()
            
        if enemy:
            active_encounter = Encounter.objects.create(
                player=player,
                enemy_type=enemy,
                enemy_hp=enemy.max_hp,
                status="ACTIVE"
            )

    enemy_hp_percent = 0
    if active_encounter and active_encounter.enemy_type.max_hp > 0:
        enemy_hp_percent = int((active_encounter.enemy_hp / active_encounter.enemy_type.max_hp) * 100)

    context = {
        'player': player,
        'enemy_hp_percent': enemy_hp_percent,
        'active_encounter': active_encounter,
    }
    
    return render(request, 'core/main.html', context)


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
        
        player_damage = 0
        enemy_damage = enemy_type.damage
        log_message = ""

        if enemy_type.name.upper() == "WITCH" and action_type == "magic":
            return JsonResponse({"error": "The dark wizard's shadow power suppresses your magic and makes it impossible to cast it!"}, status=400)

        if action_type == "magic":
            player_damage = random.randint(25, 40)
            log_message = f"🔥 You cast a blazing FIREBALL at the {enemy_type.name} for {player_damage} damage! "
            
        elif action_type == "fight":
            player_damage = random.randint(10, 20)
            if enemy_type.name.upper() == "DRAGON":
                player_damage = player_damage // 2
                log_message = f"⚔️ The dragon soars into the sky! Your sword barely scratches its hard scales for {player_damage} damage! "
            else:
                log_message = f"⚔️ You bravely slashed the {enemy_type.name} for {player_damage} damage! "
                
        elif action_type == "friend":
            player_friend = player.friends.filter(is_active=True).select_related("friend").first()
            
            if not player_friend:
                return JsonResponse({"error": "You don't have an active friend equipped!"}, status=400)
            
            friend = player_friend.friend 
            
            if friend.effect_type == "HEAL":
                heal_amount = friend.effect_value
                player.hp = min(100, player.hp + heal_amount)
                player.hp = max(0, player.hp - enemy_damage)
                log_message = f"🕊️ {friend.name} heals you for {heal_amount} HP! The {enemy_type.name} hits back for {enemy_damage} damage."
                
                game_status = "ongoing"
                if player.hp <= 0:
                    active_encounter.status = "LOST"
                    log_message += f"<br><br>☠️ You have been slain by the {enemy_type.name}..."
                    game_status = "lost"

                active_encounter.save()
                player.save()

                return JsonResponse({
                    "player_hp": player.hp,
                    "enemy_hp_percent": int((active_encounter.enemy_hp / enemy_type.max_hp) * 100) if enemy_type.max_hp > 0 else 0,
                    "log_message": log_message,
                    "game_status": game_status
                })
                
            elif friend.effect_type == "DAMAGE": # Shooter 
                player_damage = friend.effect_value + random.randint(10, 20)
                log_message = f"💥 {friend.name} strikes the {enemy_type.name} for {player_damage} damage! "
                
            elif friend.effect_type == "SPELL": # Fairy 
                player_damage = random.randint(25, 40) + (friend.effect_value * 2)
                log_message = f"✨ {friend.name} casts a powerful spell for {player_damage} damage! "
                
            elif friend.effect_type == "DEFENCE": # Hulk 
                enemy_damage = max(0, enemy_damage - friend.effect_value)
                player_damage = random.randint(1, 10) 
                log_message = f"🛡️ {friend.name} toughens you up against incoming attacks for {friend.effect_value} defence! You parried the {enemy_type.name} for {player_damage} damage! "
                
        else:
            player_damage = 0
            log_message = f"You did something unknown... "

        active_encounter.enemy_hp -= player_damage
        game_status = "ongoing"

        if active_encounter.enemy_hp <= 0:
            
            revive_key = f"zombie_revived_{active_encounter.id}"
            
            if enemy_type.name.upper() == "ZOMBIE" and not request.session.get(revive_key, False):
                active_encounter.enemy_hp = enemy_type.max_hp // 2 
                request.session[revive_key] = True 
                
                log_message += f"<br><br>🧟‍♂️ <i>Just as you were about to breathe a sigh of relief, a bone-chilling sound of skeletal restructuring came from behind... The corpse twitched bizarrely and reanimated from the dead!</i>"
                game_status = "ongoing"
                
            else:
                active_encounter.enemy_hp = 0
                active_encounter.status = "WON" 
            
                player.monsters_defeated += 1
                player.coins += enemy_type.reward_coins
            
                log_message += f"<br><br>✨ Victory! The {enemy_type.name} has been defeated! You earned {enemy_type.reward_coins} coins."
                game_status = "won"

        else:
            player.hp -= enemy_damage
            log_message += f"<br>The {enemy_type.name} hit you back for {enemy_damage} damage."
            
            if player.hp <= 0:
                player.hp = 0
                active_encounter.status = "LOST"
                log_message += f"<br><br>☠️ You have been slain by the {enemy_type.name}..."
                game_status = "lost"

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
