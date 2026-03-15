from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import InventoryItem, Item, PlayerProfile
from django.http import JsonResponse
import random
import json  
from .models import Encounter, EnemyType

@login_required
def main(request):
    if not hasattr(request.user, 'playerprofile'):
        PlayerProfile.objects.create(user=request.user)
        return redirect('game:restart')
        
    player = request.user.playerprofile
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "next_node":
            if player.current_node >= 11:
                return redirect('game:restart') 
            else:
                player.current_node += 1
                player.save()
                return redirect('game:main')
                
        elif action == "ending_dragon":
            player.current_node = 11  
            player.save()
            return redirect('game:main')
            
        elif action == "ending_hero":
            player.current_node = 12  
            player.save()
            return redirect('game:main')
       
        elif action == "open_shop":
            player.current_node += 1
            player.save()
            return redirect('game:shop') 
            
        elif action == "leave_npc":
            player.current_node += 1
            player.save()
            return redirect('game:main')


    node = player.current_node
    active_encounter = player.encounters.filter(status="ACTIVE").first()

    context = {
        'player': player,
        'game_mode': 'combat', 
        'story_texts': [],      
        'active_encounter': None,
        'enemy_hp_percent': 0,
    }

    if node == 0:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "<b>[This story is all written by Marchhare, please do not repost or modify it]</b><br><br>"
            "A deep black vortex brewed on the horizon, and the surrounding thin air pressed down so heavily I could barely breathe.<br><br>"
            "I struggled to lift my heavy eyelids, only to see a dark, fallen god half-kneeling before me. His eyes were like lifeless, pale grey glass beads—I knew it was the look of bloodthirsty desire.<br><br>"
            "Suddenly, a deafening exhale roared in my ears. As my vision focused, the fallen god was nowhere to be seen; sprawled before me was a colossal dragon. At that exact moment, my gaze locked with its blood-red pupils. The profound darkness and malice harboring in the beast's eyes instantly seized my throat. I opened my mouth to cry for help, but could only let out a feeble, breathless gasp.",
            
            "I jolted awake, belatedly realizing my shirt was drenched in cold sweat. I had lost count of how many times I'd had this abrupt, disjointed dream. Ever since I read that book about the red dragon in the Royal Library, the same nightmare would ambush me in the dead of night.<br><br>"
            "Absurd as it sounds, half a month ago, the Grand Arcanist before the royal throne toyed with his crystal ball and told me these damned nightmares were the omen of a dragonslayer's awakening.<br><br>"
            "Shortly thereafter, a royal decree dubbed me a Dragonslayer Knight, and I set out alone on a journey to hunt the beast. There was no honor guard cheering me on like in the adventure tales, nor was anyone willing to accompany me into the unknown darkness. The only companion on my entire journey was the solitary, reckless courage I held when I first accepted this quest.",
            
            "Everyone dreams of treading upon the dragon's corpse to become a hero of the realm, and I was no exception.<br><br>"
            "For as long as I can remember, evil forces have threatened the lives of everyone around me. Truth be told, there have been many dragonslayers before me. In the beginning, the people watched them march off to crusade against the beast, their eyes filled with hope and blessings. Yet, day after day, the triumphant news of a returning hero never came; instead, there were only grim tidings of the dragon repeatedly ravaging the kingdom's borders. Those previous slayers faded into silence years ago, their fates unknown. By the time the mantle fell to my generation, even the grand send-off ceremonies had been abandoned.<br><br>"
            "Perhaps what is more terrifying than the dragon is the repeated shattering of hope.<br><br>"
            "I clenched my fists, silently making a vow in that resting cave—<br><br>"
            "I will make the spark of hope flare to life once more in my hands.",
            
            "The patter of falling rain echoed from outside the cave; another gloomy downpour.<br><br>"
            "It was too dark when I chose this cave last night to notice my surroundings. Looking around now, I realized that just a short distance outside stood a graveyard thick with tombstones. My mouth twitched as I turned away, forcing myself to stay calm. While it was true that under the influence of dark magic, most skeletons haunted graveyards on rainy days, surely my luck wasn't so rotten that I'd encounter monsters before even making it halfway along the map's path?<br><br>"
            "Just as I was packing my pathetically sparse knapsack, a spine-chilling sound drifted from the direction of the graveyard behind me—like the sound of fingernails viciously scraping across dry bark.<br><br>"
            "My heart pounded like a war drum. Gritting my teeth, I whipped my head around and was met with the very sight I dreaded most: a skeleton, trembling as it clawed its way out of the earth, lunging at me with an eerie green glow in its empty eyes.<br><br>"
            "<span style='color: #8B0000; font-weight: bold;'>(Tutorial: Please click the Fight button to perform normal attack, and click the Magic button to select magic attack or heal yourself)</span>"
        ]

    elif node == 1:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="SKULL").first()
            if not enemy:
                enemy = EnemyType.objects.first() 
                
            if enemy:
                active_encounter = Encounter.objects.create(
                    player=player,
                    enemy_type=enemy,
                    enemy_hp=enemy.max_hp,
                    status="ACTIVE"
                )
                
    elif node == 2:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "The skeleton's bones scattered across the ground, crumbling into a pile of ash. I couldn't help but let out a long sigh of relief.<br><br>Just then, the clatter of wooden cart wheels echoed from the nearby woods.",
            "A mysterious merchant, draped in a heavy cloak that obscured his face, stopped before me.<br><br>\"Heh, well done, young dragonslayer! But the road ahead is still long, and that scrap metal you're wearing won't last you to the dragon's lair.\" He chuckled hoarsely and pulled back the canvas on his cart, revealing a dazzling array of potions and glowing magic scrolls.",
            "\"I've got some good stuff here. Every time you defeat those pesky monsters, the loot they drop can be traded with me for rare collectibles. As long as you have enough coins, I can even get you a demon's tear.\"<br><br><span style='color: #8B0000; font-weight: bold;'>(Tip: You can click the Trade button ahead or the Shop button in the top right corner. After shopping, return to this page to continue your journey.)</span>"
        ]

    elif node == 3:
        context['game_mode'] = 'npc'
        context['npc_name'] = 'Mysterious Wandering Merchant'
        context['npc_image'] = 'merchant.png' 
        context['npc_dialogue'] = (
            "Heh heh heh... A Dragonslayer Knight, isn't it? "
            "It has been years since I saw someone foolish enough to walk this path. "
            "The road ahead is paved with bones. Care to buy something to extend your miserable life?"
        )

    elif node == 4:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Bidding farewell to the mysterious merchant, I continued down the muddy path.<br><br>A crow outside the barn let out a sudden shriek. I snapped back to reality, my eyes locked on a rotting hand thrusting out from the ruined, withered blossoms.",
            "I tightened my grip on my weapon, bracing for the fight. Having accepted the plea of the unarmed and defenseless, I could not afford to show a sliver of cowardice."
        ]
        
    elif node == 5:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="ZOMBIE").first()
            if not enemy:
                enemy = EnemyType.objects.first() 
                
            if enemy:
                active_encounter = Encounter.objects.create(
                    player=player,
                    enemy_type=enemy,
                    enemy_hp=enemy.max_hp,
                    status="ACTIVE"
                )
                
    elif node == 6:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Thick mist veiled the swamp. I stepped into a muddy hollow, and no matter how hard I struggled, I couldn't pull my trapped boot free. Just as frustration took hold, the vines that had been lying dormant nearby silently coiled around my ankle. I tried to dispel them with an incantation, but it backfired; I was bound fast to the spot, entirely immobilized.<br><br>"
            "A light, melodic chuckle drifted closer through the gloom. I glared furiously at the dark wizard who materialized from the mist, but he ignored my silent protest. Stepping close, he looked me up and down with brazen amusement.",
            
            "\"Is all this truly worth it?\" he began, waving a hand to conjure a mirage before my eyes. In the illusion, the king was immersed in endless revelry and feasts, while the city guards slacked off in gluttony and sloth. He smiled faintly, tapping a finger against my temple. \"You are brave, but to come all this way for these people... it isn't worth it.\"<br><br>"
            "I froze. Those illusions took root and sprouted in my mind like magic beans, faintly shaking my unwavering resolve. Barely surviving countless brushes with death to get here—was it really worth it? But this seed of doubt did not last long. The faces of the companions I had met on this journey leaped vividly back into my mind, and the words they had spoken to me slowly filled my heart.",
            
            "When I first embarked on this journey, I was fearful and cowardly. But now, I am no longer the person I used to be. Even if it isn't for anyone else, just to ensure this bitter trek wasn't made in vain, I must point my sword at the dragon and challenge it. Not to mention—<br><br>"
            "\"Where there are hedonists, there are strivers; where there are cowards, there are the brave. You cannot blind yourself to the pristine light worth admiring and protecting just because there is filth in the world.\" A cold scoff escaped my nose. \"Did you think I haven't questioned if it's worth it? I've asked myself countless times, and my answer has always been the exact same.\"<br><br>"
            "I lunged at the wizard. \"I only care about my true heart, and it tells me that all of this is worth it.\"<br><br>"
            "<span style='color: #8B0000; font-weight: bold;'>(Warning: The dark wizard's shadow power suppresses your magic, and healing/magic spells cannot be used in this battle!)</span>"
        ]

    elif node == 7:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="witch").first()
            if not enemy:
                enemy = EnemyType.objects.first()
                
            if enemy:
                active_encounter = Encounter.objects.create(
                    player=player,
                    enemy_type=enemy,
                    enemy_hp=enemy.max_hp,
                    status="ACTIVE"
                )
                
    elif node == 8:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "The shattered signpost bore the final, desperate words carved by a previous hero, as a biting wind howled through the hall.<br><br>I tightened my grip on the hilt of my sword, stepped over a sea of bleached bones, and pushed open the massive bronze doors.",
            "Coiled upon the throne sat the sky-blotting, pureblood red dragon.<br><br>It slowly opened its dark-gold slitted pupils, eyeing me—its uninvited guest—with mocking amusement. The air was thick with the stench of sulfur and despair. The final trial had begun!"
        ]

    elif node == 9:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="dragon").first()
            if not enemy:
                enemy = EnemyType.objects.first()
            if enemy:
                active_encounter = Encounter.objects.create(
                    player=player, 
                    enemy_type=enemy, 
                    enemy_hp=enemy.max_hp, 
                    status="ACTIVE"
                )

    elif node == 10:
        context['game_mode'] = 'decision'  

    elif node == 11:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "As if possessed, I walked toward the dragon's corpse and reached out to gouge out the dark-gold dragon eye radiating a beguiling glow.<br><br>In an instant, a frenzied dark power surged through my veins. My skin began to sprout hard, dark-red scales; the bones in my back tore apart violently as a pair of sky-blotting fleshy wings burst from my flesh.",
            "Gazing down at the insignificant human capital, a deafening roar tore from my throat... The dragonslayer had ultimately become the next evil dragon to rule the world.<br><br><span style='color:darkred; font-weight:bold;'>【 BAD ENDING: Gaze of the Abyss 】</span><br><br>(Press Enter to restart)"
        ]

    elif node == 12:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Resisting the eerie temptation radiating from the dragon's eye, I raised my staff, channeled every last drop of my mana, and unleashed the most scorching fireball upon the dragon's corpse.<br><br>The raging inferno reduced the dragon's bones and its wicked curses to ashes. Sunlight finally pierced through the gloom that had shrouded the royal capital for years.",
            "I dragged my exhausted body back to the town. This time, there was no superficial honor guard—only the heartfelt cheers and warm tears of the reborn commoners... The spark of hope had finally been rekindled in this era.<br><br><span style='color:goldenrod; font-weight:bold;'>【 TRUE ENDING: Breaking Dawn 】</span><br><br>(Press Enter to restart)"
        ]

    if context['game_mode'] == 'combat':
        if active_encounter:
            context['active_encounter'] = active_encounter
            if active_encounter.enemy_type.max_hp > 0:
                context['enemy_hp_percent'] = int((active_encounter.enemy_hp / active_encounter.enemy_type.max_hp) * 100)
        else:
            
            messages.error(request, "A disturbance in the magical weave occurred. The world has reset.")
            return redirect('game:restart')
    
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

        if enemy_type.name.upper() == "WITCH" and action_type == "magic":
            return JsonResponse({"error": "The dark wizard's shadow power suppresses your magic and makes it impossible to cast it!"}, status=400)
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
    player.current_node = 0  
    player.monsters_defeated = 0

    player.save()
    player.encounters.all().delete()
    
    player.encounters.filter(status__in=["ACTIVE", "LOST"]).delete()
    
    
    return redirect('game:main')
