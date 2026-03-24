from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import InventoryItem, Item, PlayerProfile
from django.http import JsonResponse
import random
import json  
from .models import Encounter, EnemyType, Signpost,FriendType, PlayerFriend

@login_required
def main(request):
    if not hasattr(request.user, 'playerprofile'):
        PlayerProfile.objects.create(user=request.user)
        return redirect('/game/restart/')
        
    player = request.user.playerprofile
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "next_node":
            if player.current_node in [121, 122]:
                player.current_node = 13
                player.save()
                return redirect('game:main')
            elif player.current_node in [201, 202,214,215]:
                player.current_node = 23
                player.save()
                return redirect('game:main')
            elif player.current_node == 203:
                player.current_node = 21
                player.save()
                return redirect('game:main')
            elif player.current_node in [231, 232]:
                player.current_node = 24
                player.save()
                return redirect('game:main')
            elif player.current_node in [241, 242]:
                player.current_node = 25
                player.save()
                return redirect('game:main')
            elif player.current_node == 25:
                player.current_node = 251
                player.save()
                return redirect('game:main')
            elif player.current_node == 251:
                player.current_node = 26
                player.save()
                return redirect('game:main')
            elif player.current_node == 29:
                player.current_node = 291
                player.save()
                return redirect('game:main')
            elif player.current_node == 291:
                player.current_node = 30
                player.save()
                return redirect('game:main')
            elif player.current_node >= 33:
                return redirect('/game/restart/') 
            else:
                player.current_node += 1
                player.save()
                return redirect('game:main')
                
        elif action == "ending_dragon":
            player.current_node = 33  
            player.save()
            return redirect('game:main')
            
        elif action == "ending_hero":
            player.current_node = 34  
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

        elif action == "giant_opt1":
            player.current_node = 121
            player.hp = max(1, player.hp - 20) 
            player.save()
            return redirect('game:main')

        elif action == "giant_opt2":
            player.current_node = 122
            player.save()
            
            friend_obj, _ = FriendType.objects.get_or_create(name="Hulk", defaults={"effect_type": "DAMAGE", "effect_value": 15})
            pf, _ = PlayerFriend.objects.get_or_create(player=player, friend=friend_obj)
            pf.is_active = True
            pf.save()
            
            return redirect('game:main')

        elif action == "guard_opt1":
            player.current_node = 201
            request.session['visited_village'] = False
            player.save()
            return redirect('game:main')

        elif action == "guard_opt2":
            player.current_node = 202
            player.hp = max(1, player.hp - 10) 
            request.session['visited_village'] = False 
            player.save()
            return redirect('game:main')

        elif action == "guard_opt3":
            player.current_node = 203
            request.session['visited_village'] = True 
            player.save()
            
            friend_obj, _ = FriendType.objects.get_or_create(name="Shooter", defaults={"effect_type": "DAMAGE", "effect_value": 10})
            pf, _ = PlayerFriend.objects.get_or_create(player=player, friend=friend_obj)
            pf.is_active = True
            pf.save()
            
            return redirect('game:main')

        elif action == "hunter_opt1":
            player.current_node = 231
            player.save()
            return redirect('game:main')

        elif action == "hunter_opt2":
            player.current_node = 232
            player.hp = 1 
            player.save()
            return redirect('game:main')

        elif action == "fairy_opt1":
            player.current_node = 241
            player.save()
            return redirect('game:main')

        elif action == "fairy_opt2":
            player.current_node = 242
            player.hp = min(player.hp + 20, 100) 
            player.save()
            friend_obj, _ = FriendType.objects.get_or_create(name="Fairy", defaults={"effect_type": "HEAL", "effect_value": 25})
            pf, _ = PlayerFriend.objects.get_or_create(player=player, friend=friend_obj)
            pf.is_active = True
            pf.save()
            return redirect('game:main')
        
        elif action == "leave_signpost":
            message = request.POST.get("signpost_message", "").strip()
            ending_type = request.POST.get("ending_type", "Unknown")
            
            if message:
                Signpost.objects.create(message=message, ending_type=ending_type)
            
            return redirect('/game/restart/')

        elif action == "submit_riddle":
            answer = request.POST.get("riddle_answer", "").strip().lower()
            
            if player.current_node == 21 and answer == "fear":
                player.current_node = 212
            elif player.current_node == 212 and answer == "death":
                player.current_node = 213
            elif player.current_node == 213 and answer == "hope":
                player.current_node = 214
                
                friend_obj, _ = FriendType.objects.get_or_create(name="Phoenix", defaults={"effect_type": "HEAL", "effect_value": 20})
                pf, _ = PlayerFriend.objects.get_or_create(player=player, friend=friend_obj)
                pf.is_active = True
                pf.save()
            else:
                player.current_node = 215
                player.coins += 10
                
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
            "<b>【This story was handwritten by March Hare. Please do not modify or redistribute it.】</b><br><br>"
            "A deep black vortex brewed on the horizon, and the surrounding thin air pressed down so heavily I could barely breathe.<br><br>"
            "I struggled to lift my heavy eyelids, only to see a dark, fallen god half-kneeling before me. His eyes were like lifeless, pale grey glass beads—I knew it was the look of bloodthirsty desire.<br><br>"
            "Suddenly, a deafening exhale roared in my ears. As my vision focused, the fallen god was nowhere to be seen; sprawled before me was a colossal dragon. At that exact moment, my gaze locked with its blood-red pupils. The profound darkness and malice harboring in the beast's eyes instantly seized my throat. I opened my mouth to cry for help, but could only let out a feeble, breathless gasp."
        ]

    elif node == 1:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I jolted awake, belatedly realizing my shirt was drenched in cold sweat. I had lost count of how many times I'd had this abrupt, disjointed dream. Ever since I read that book about the red dragon in the Royal Library, the same nightmare would ambush me in the dead of night.<br><br>"
            "Absurd as it sounds, half a month ago, the Grand Arcanist before the royal throne toyed with his crystal ball and told me these damned nightmares were the omen of a dragonslayer's awakening.<br><br>"
            "Shortly thereafter, a royal decree dubbed me a Dragonslayer Knight, and I set out alone on a journey to hunt the beast. There was no honor guard cheering me on like in the adventure tales, nor was anyone willing to accompany me into the unknown darkness. The only companion on my entire journey was the solitary, reckless courage I held when I first accepted this quest."
        ]

    elif node == 2:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Everyone dreams of treading upon the dragon's corpse to become a hero of the realm, and I was no exception.<br><br>"
            "For as long as I can remember, evil forces have threatened the lives of everyone around me. Truth be told, there have been many dragonslayers before me. In the beginning, the people watched them march off to crusade against the beast, their eyes filled with hope and blessings. Yet, day after day, the triumphant news of a returning hero never came; instead, there were only grim tidings of the dragon repeatedly ravaging the kingdom's borders. Those previous slayers faded into silence years ago, their fates unknown. By the time the mantle fell to my generation, even the grand send-off ceremonies had been abandoned.<br><br>"
            "Perhaps what is more terrifying than the dragon is the repeated shattering of hope.<br><br>"
            "I clenched my fists, silently making a vow in that resting cave—<br><br>"
            "I will make the spark of hope flare to life once more in my hands."
        ]

    elif node == 3:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "The patter of falling rain echoed from outside the cave; another gloomy downpour.<br><br>"
            "It was too dark when I chose this cave last night to notice my surroundings. Looking around now, I realized that just a short distance outside stood a graveyard thick with tombstones. My mouth twitched as I turned away, forcing myself to stay calm. While it was true that under the influence of dark magic, most skeletons haunted graveyards on rainy days, surely my luck wasn't so rotten that I'd encounter monsters before even making it halfway along the map's path?"
        ]

    elif node == 4:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "My mouth tasted like cold, hard iron. My nails dug fiercely into my palms. There was no other way now—I had to fight. My weapon seemed to hear my inner voice, trembling in response to my resolve. I was just about to turn my head when a sudden sharp pain pierced my mind. In a flash of lightning, I heard a voice speaking directly into my head, a voice identical to the one in my nightmares about the dragon."
        ]

    elif node == 5:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "\"Great dragonslayer,\" the voice hissed in marvel. \"You finally walked this path, didn't you?\"<br><br>"
            "The voice in my head seemed to bore out from the very depths of my soul, seeing my panic and unease with utter clarity. \"This is merely the first step of the trial. I thought you would be braver.\"<br><br>"
            "I heard the undisguised mockery in that tone. Anger surged into my heart as I abruptly turned to face the skeleton slowly marching toward me. A faint taste of rust lingered on my tongue. The fear in my heart was replaced by a competitive instinct, leaving only one thought in my mind.<br><br>"
            "Prove myself. Defeat this damn bag of bones.<br><br>"
            "\"That's right,\" the voice clicked its tongue. \"Use your Fight and Magic buttons to defeat him.\" It sneered. \"If you still have the strength, that is.\""
        ]

    elif node == 6:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="SKULL").first()
            if not enemy:
                enemy = EnemyType.objects.first() 
            if enemy:
                active_encounter = Encounter.objects.create(player=player, enemy_type=enemy, enemy_hp=enemy.max_hp, status="ACTIVE")

    elif node == 7:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I took a deep breath, drew the longsword from my waist, and swung. Accompanied by rusty yet forceful slashes, the crisp sound of shattering bones echoed before the cave. The skeleton's claws tore at my hand, but seizing the opening of the monster's stiff movement, I gripped my sword with both hands and shattered its skull with all my might.<br><br>"
            "The voice in my head quieted down, and in my daze, I only heard a faint chuckle."
        ]

    elif node == 8:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "The adrenaline faded, leaving me anxious to resolve the myriad of questions in my mind. I whispered to that mysterious soul from nowhere. I had countless things to ask: about his identity, why he chose me, and the legends of the dragons. But the soul was temperamental; my repeated attempts to converse with him yielded nothing in return.<br><br>"
            "My heart sank, the illusion of companionship shattered. In an instant, I was alone again, as if the voice had been nothing but a hallucination. The path of a dragonslayer is solitary, a lonely trudge forward.<br><br>"
            "The sound of broken bells pierced through the rain. I instinctively tightened my grip on my weapon. This place was desolate, unlikely to see travelers. Could it be that I had attracted a legion of skeletons?"
        ]

    elif node == 9:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Through the rain, a dim lantern suddenly lit up. A short old man wrapped in a heavy cloak had appeared out of nowhere under a nearby tree. I noticed several delicate bells tied to the tail of his horse, ringing out a strange melody with every movement. The hood obscured his face, and his flamboyant presence did not seem like an ordinary passerby.<br><br>"
            "Sensing danger, I was about to take a combat stance, but the stranger laughed first.<br><br>"
            "\"Hold your weapons, Sir Knight.\" His voice carried the icy winds of the North and the gritty taste of the badlands. Realizing I still stood motionless with suspicion, he stepped aside to reveal the packs on his horse. \"I am but a passing merchant. Why soil a brave knight's hands with my blood?\" Yet, there was no respect in his tone. \"Why doesn't the Knight peruse my wares and spare a few coins for my wine?\"<br><br>"
            "\"He's asking to trade with you,\" the long-silent soul spoke up lazily, not giving me a chance to interrupt. \"Use the Shop button to buy something, though from what I see, your choices are quite limited.\"<br><br>"
            "He was mocking my lack of gold. I scoffed inwardly—if this soul were some rich, powerful hedonist, why would he be wandering around me?"
        ]

    elif node == 10:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "As he drew closer, I indeed saw the emblem of a merchant caravan on his bells. Caravans usually traveled in packs; I wondered why he was alone. Strangely, this thought put me slightly at ease—a mutual understanding between solitary travelers.<br><br>"
            "While carefully inspecting his goods, I struck up a casual conversation. \"Wine? Is there a village nearby?\"<br><br>"
            "The merchant stroked his horse's mane, his eyes glancing maliciously into the cave. Following his gaze, I saw my own steed and firmly refused, \"Not for sale.\"<br><br>"
            "The merchant sighed in disappointment, but he didn't ignore my question. \"Follow this road straight ahead. You'll see an abandoned barn. Behind it is a winding path, and at the end of that path is a village.\"<br><br>"
            "\"This isn't far from the dragon's lair. I thought it would be completely deserted,\" I said, taking out my map to mark the location, confused.<br><br>"
            "The merchant fell silent. I belatedly realized he was waiting for payment to answer my next question. Watching me pat my pockets empty, he merely smiled and tapped the most valuable thing on me—my iron armor. \"Go on, Dragonslayer. We shall meet again soon enough.\"<br><br>"
            "Humming an unknown tune, he rode off into the distance."
        ]

    elif node == 11:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "The rain soon stopped. I mounted my horse and galloped along the muddy path toward the location on the map. Luck seemed to be on my side as hooves trotted briskly onto the main road, passing dense, overlapping thickets. Just as the road began to open up, my steed suddenly let out a startled snort and ground to a halt.<br><br>"
            "The massive momentum nearly threw me from the saddle. This abnormal behavior raised my suspicions. Looking closely, I saw a row of colossal footprints imprinted in the mud ahead. Savages? I looked around frantically, but saw only layers of trees and a sprawling canopy of green; there were no signs of wild men.<br><br>"
            "As I hesitated, a roar echoed from deep within the forest, drawing closer and startling a flock of birds into the sky. When the birds scattered, heavy footsteps pounded in my ears. I gripped my weapon, ready for battle. The first thing to catch my eye was the newcomer's green skin. But when I looked up to see his face, I was shocked to find a towering, massive green giant."
        ]

    elif node == 12:
        context['game_mode'] = 'interactive_npc'
        context['npc_name'] = 'Angry Green Giant (Hulk)'
        context['npc_image'] = 'hulk.png' 
        context['npc_dialogue'] = (
            "His muscles bulged like boulders, and his stomach let out a thunderous growl. He looked incredibly angry and hungry.\n\n"
            "Noticing my approach, he hoisted a massive boulder effortlessly and roared, 'Hulk smash! Leave Hulk alone!'"
        )
        context['choices'] = [
            {'text': 'Draw your sword: "I am a Dragonslayer, I fear no one!"', 'action': 'giant_opt1'},
            {'text': 'Lower weapon and offer rations: "You look starving. Have some food."', 'action': 'giant_opt2'}
        ]

    elif node == 121:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I drew my sword, ready to face this behemoth. But before I could even chant a spell, the green giant let out a deafening roar and smashed the ground with his fists.",
            "The shockwave sent me flying, crashing heavily into a tree trunk. Coughing up blood, I watched as the giant leaped into the sky and disappeared into the clouds.",
            "<span style='color: darkred; font-weight: bold;'>[ 💥 WARNING: Hulk smashed! You lost 20 HP! ]</span>"
        ]

    elif node == 122:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I slowly lowered my sword, pulled out the dried meat and bread from my knapsack, and tossed them to the giant.",
            "The green behemoth sniffed the food cautiously before devouring it in one massive bite. The furious glint in his eyes softened, replaced by a childlike satisfaction.",
            "\"Puny knight is good. Hulk likes puny knight,\" he grunted, pounding his massive chest. \"Hulk will help puny knight smash the winged lizard!\"",
            "<span style='color: green; font-weight: bold;'>[ 🤝 SUCCESS: Hulk has joined your party! You can now call upon his strength using the 'Friend' button in battles! ]</span>"
        ]

    elif node == 13:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Emerging from the dense forest, I finally saw the light of day. The barn the merchant mentioned stood quietly in a desolate, ruined reed field. As I rode forward, a mournful wail pierced the air. On the grass before the barn huddled two small figures dressed as commoners. One of them yelled, wildly swinging what looked like a tree branch.<br><br>"
            "Spotting the shambling creature closing in on them, I spurred my horse into a gallop.<br><br>"
            "A putrid zombie unhinged its massive jaw, lunging at the unarmed civilians. It missed, its milky, dead eyes staring blankly at me. I struck first, kicking it squarely in the jaw and sending the subterranean monstrosity crashing to the ground.<br><br>"
            "\"Save us!\" the two cried out, clinging to me like a lifeline. They stared suspiciously at the fallen zombie. \"Is it dead?\"<br><br>"
            "\"Far from it,\" I muttered, watching a rotting hand burst through a patch of withered flowers. I gripped my weapon tightly. \"Stay behind me.\"<br><br>"
            "\"Not bad,\" the soul suddenly chimed in. He clearly wouldn't miss a chance to tease me. \"You're actually starting to look the part.\""
        ]

    elif node == 14:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="ZOMBIE").first()
            if not enemy:
                enemy = EnemyType.objects.first() 
            if enemy:
                active_encounter = Encounter.objects.create(player=player, enemy_type=enemy, enemy_hp=enemy.max_hp, status="ACTIVE")

    elif node == 15:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "This zombie exuded a nauseating stench of rot; every swipe carried lethal force. I nimbly rolled to dodge its heavy blow and pierced its chest with a backhand thrust. Black blood spewed out as the massive body crashed to the ground.<br><br>"
            "Just as I was about to breathe a sigh of relief, a bone-chilling sound of skeletal restructuring came from behind. The corpse that should have been dead twitched bizarrely. Dragging its mangled half-body, the rotting flesh around its wound healed halfway, and it lunged at me again with an inhuman roar.<br><br>"
            "\"Damn it.\" I gritted my teeth and raised my sword without hesitation. This time, I gave it my all, directly severing its head, completely ending the agony of this walking corpse."
        ]

    elif node == 16:
        context['game_mode'] = 'story'
        coin_key = f"received_node_16_coins_{player.id}"
        if not request.session.get(coin_key, False):
            player.coins += 20
            player.save()
            request.session[coin_key] = True
        context['story_texts'] = [
            "\"Sir Knight!\" Once I confirmed the zombie was motionless, the two commoners peeked out from behind me, still trembling. \"You saved us.\" Tear tracks stained their faces as their legs gave out, almost kneeling before me again.<br><br>"
            "I quickly reached out, grabbing their arms to pull them up. \"It is my duty.\" To think I'd ever have the chance to say such a line—an unfamiliar emotion rippled through my heart. But before I could process it, a tattered coin pouch was shoved into my hands.<br><br>"
            "\"I can't—\" I shook my head, but they pressed the pouch into my palm, insisting I take it. Judging by their clothes, they were no wealthier than I; this was likely their life savings. I felt I didn't deserve it.<br><br>"
            "\"Don't deserve it?\" The lingering soul scoffed, and I could vividly imagine his disdainful glare. \"You saved their lives. Even if they worked as your beasts of burden, you'd deserve it.\"<br><br>"
            "<span style='color: gold; font-weight: bold;'>[ 💰 You received 20 Coins! ]</span>"
        ]

    elif node == 17:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "One of the commoners looked up, eyes gleaming. \"My Lord, what brings you to these parts?\"<br><br>"
            "\"An unknown merchant told me there was a village nearby.\" I pulled out the map and pointed to the mark. \"Are you residents there?\"<br><br>"
            "\"Yes! We can take you there to rest.\" They nodded eagerly. But as they noticed the mark at the end of my map, their faces drained of color. \"My Lord... are you seeking the dragon?\" Their voices trembled, as if struck by immense terror.<br><br>"
            "\"I am a dragonslayer.\" I showed them my knight's crest. \"I assumed you had seen others of my kind.\"<br><br>"
            "\"We have... of course we have,\" the commoner choked back a sob, pointing a trembling finger at the zombie sunken in the mud. \"It had a gold tooth right on its canine. I would never forget that.\"<br><br>"
            "I stood frozen, watching the two commoners bury their faces and weep. For a moment, I couldn't find a single word of comfort. A sudden chill swept through my veins as the image of the zombie's cloudy, unyielding eyes flashed in my mind.<br><br>"
            "Nearby, a raven let out a sharp cry. Several scavengers answered the call, flocking over to eagerly peck at the stiffened bones of the former dragonslayer."
        ]

    elif node == 18:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "\"Damn dinosaurs.\" A sharp shout shattered the heavy silence. To my surprise, the familiar sound of bells rang out again. The merchant pulled a bone whistle from nowhere and blew a single, piercing note that sent the scavengers fleeing in panic.<br><br>"
            "I looked at him gratefully, but he just dramatically opened his palms. \"A free favor for you, Lord Dragonslayer. No charge this time.\"<br><br>"
            "\"Where are the dinosaurs?\" I asked, confused, scanning the desolate plains for the legendary prehistoric behemoths. But there were only us insignificant humans; there was no sign of such colossal beasts.<br><br>"
            "The merchant pocketed the whistle, his tone laced with disgust. \"Those blasted scavenger birds. They are degenerate dinosaurs.\"<br><br>"
            "It was the first time I'd heard such an analogy. Without the leisure to debate species evolution with him, I eyed the packs on his horse and couldn't help but ask, \"Have you been following me?\"<br><br>"
            "\"No.\" The merchant shook his head. \"Look.\" He reached out and patted my shoulder, but his fingers passed straight through my body. \"I merely sensed a customer's desire to trade, so I materialized nearby.\"<br><br>"
            "\"No wonder you don't travel with the caravans.\" I looked at him, a slight pang in my chest. \"You're a wraith.\"<br><br>"
            "\"Don't be so hurtful with your words,\" the merchant replied nonchalantly, unfolding his pack to reveal gleaming wares. \"I was just starting to enjoy trading with you.\""
        ]

    elif node == 19:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Bidding farewell to the merchant, the two commoners guided me to their village. It was far more peaceful than I had imagined, complete with sturdy walls and aqueducts. Were it not for the massive dark clouds swirling over the distant peaks, I could hardly believe this settlement lived under the shadow of the Dragon's Valley.<br><br>"
            "<i>Have they never thought of moving?</i> The question lingered in my mind, but I couldn't bring myself to ask.<br><br>"
            "\"Stupid question,\" the soul mocked in my head. \"If they could leave, they would have run long ago.\"<br><br>"
            "\"Speaking of stupid questions,\" I replied, surprisingly patient enough to converse calmly with this obnoxious presence. \"Are you willing to tell me now? Who are you? Why me?\"<br><br>"
            "\"I approach every dragonslayer,\" the soul answered, unusually forthcoming. \"You can think of me as your soul's envoy.\"<br><br>"
            "\"My soul's envoy?\" I scoffed without hesitation. \"More like some wandering ghost from that cave. Drifting alone for so long, no wonder your temper is so foul.\"<br><br>"
            "\"I just didn't believe you could make it this far.\" The soul didn't erupt in anger, speaking almost reluctantly. \"The dragonslayers I saw before you—\"<br><br>"
            "He fell silent abruptly, seemingly realizing he shouldn't mention them. This only piqued my curiosity. \"You followed many dragonslayers? Do you remember if you had any unfulfilled wishes before you died? Maybe I can help you, so you don't have to remain a wandering ghost.\"<br><br>"
            "\"I told you, I'm not a wraith,\" the entity ground out through gritted teeth. I thought he would ignore me for a long time after that. But as I stepped deeper into the village, his voice echoed again, as light as a sigh.<br><br>"
            "\"I have long forgotten my name.\""
        ]

    elif node == 20:
        context['game_mode'] = 'interactive_npc'
        context['npc_name'] = 'Village Guard Captain'
        context['npc_image'] = 'captain.png' 
        context['npc_dialogue'] = (
            "The captain of the village guard stood before the gates, his hawk-like eyes scanning me from head to toe. \"You were sent by the wizards, weren't you?\"\n\n"
            "\"Father! He saved us,\" my companion cried out. \"The wizards would only watch us get—\"\n\n"
            "\"But a wizard could also disguise himself as a valiant knight.\" The captain sneered, ignoring the protests. He suddenly drew the broadsword from his waist. The heavy blade whistled through the air, stopping mere inches from my throat. I could even smell the accumulated stench of blood on the steel.\n\n"
            "\"Truth never spills from a wizard's mouth. I bear the safety of this entire village; I cannot trust lightly.\" The captain's eagle eyes locked onto mine, searching for any trace of panic. \"Do you have any last words?\""
        )
        context['choices'] = [
            {'text': 'Say nothing. Stare dead into his eyes.', 'action': 'guard_opt1'},
            {'text': 'Take out the knight\'s crest and explain his mistake.', 'action': 'guard_opt2'},
            {'text': '"I only die at the hands of one who defeats me." Challenge him.', 'action': 'guard_opt3'}
        ]

    elif node == 201:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Facing the frost-radiating broadsword at my throat, I remained utterly silent. My body didn't flinch; I merely stared back into those sharp, hawk-like eyes. Having danced on the edge of life and death countless times, my gaze held no fear of mortality—only a deathly, icy stillness.<br><br>"
            "The captain locked eyes with me for a long time. His sword hand twitched slightly. Finally, he let out a cold laugh, abruptly retracting the blade. He slammed the hilt against my chest, knocking me back two steps.<br><br>"
            "\"Only a suicidal madman would have a gaze like that. Wizards aren't that stupid,\" he cast a cold glance at me, his tone devoid of warmth. \"Consider yourself lucky. You saved my son's life, so I won't kill you today. But that doesn't mean I trust you. Now, take your weapons and get out of my sight. Don't let me catch you here again.\""
        ]

    elif node == 202:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Suppressing the chill at my throat, I slowly reached into my pack and pulled out the dirt-and-blood-stained knight's crest, holding it before his eyes. \"You have the wrong person. I am a Dragonslayer Knight, bound by royal decree. I am no wizard.\"<br><br>"
            "The captain's gaze lingered on the crest for a fraction of a second before he let out a mocking sneer. He violently swung the flat of his blade, brutally striking my wrist and knocking me back. The crest nearly slipped from my grasp.<br><br>"
            "\"What does a piece of scrap metal prove? Scavengers can pull hundreds of these trinkets off corpses on a battlefield!\" He looked at me with pure disdain. \"Stow your parlor tricks. For the sake of my son's life, I'll leave your corpse intact today. Disappear from my gates immediately, or next time, my blade will slice straight through your windpipe.\"<br><br>"
            "<span style='color: darkred; font-weight: bold;'>[ 🩸 WARNING: The captain struck you! You lost 10 HP! ]</span>"
        ]

    elif node == 203:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "The stinging pain at my throat didn't break me; instead, it ignited the warrior's bloodlust buried deep within. I didn't back down. Instead, I tilted my chin up against his edge, battle intent burning in my eyes.<br><br>"
            "\"I have no last words,\" my voice was as cold as forged ice, \"because I only die at the hands of one who can defeat me. If you don't believe me, draw your sword and test me!\"<br><br>"
            "Before my words even settled, I violently drew my weapon, parrying the broadsword away from my neck. The ear-piercing clash of metal exploded at the gates, sparks flying. The captain clearly hadn't expected me to counterattack so fiercely from such a disadvantage. A flash of shock crossed his eyes, but years of combat instinct had him instantly swinging back.<br><br>"
            "After several intense exchanges, there was no flashy magic—only the pure collision of strength and muscle memory. My desperate, completely unhinged fighting style finally forced the captain to take a half-step back after a heavy clash.<br><br>"
            "He panted heavily, suddenly sheathing his broadsword. \"Hahaha! That's the spirit!\" A booming laugh erupted from his rugged face, all previous hostility vanishing into thin air. \"The combat forms taught by the Royal Knights haven't changed in over a decade.\"<br><br>"
            "He stepped forward, clapping my shoulder with astonishing force. \"I misjudged you, Dragonslayer. Forgive a father's caution.\" He paused, pressing a bone whistle into my hand. \"I admire a brave soul like you. You bested me. In return, I'm willing to lend a hand when you face the dragon. Whenever you need me, blow this, and I will fight by your side.\"<br><br>"
            "<span style='color: green; font-weight: bold;'>[ 🤝 SUCCESS: Guard Captain Shooter has joined your party! ]</span>"
        ]

    elif node == 21:
        context['game_mode'] = 'riddle'
        context['npc_name'] = 'Mysterious Bard'
        context['npc_image'] = 'bard.png'
        context['riddle_question'] = "The village tavern was thick with the scent of cheap rum and roasted meat. A bard wearing a wide-brimmed felt hat unceremoniously sat across from me. \n\n\"Listen well.\" The bard strummed a chord, his voice suddenly dropping into an ancient cadence. \n\n\"First riddle: What is born without flesh or blood, yet can devour armies; has no voice, yet can make the most fearless warrior tremble?\""
        if request.session.pop('riddle_wrong', False):
            context['riddle_error'] = "The bard shakes his head. 'Wrong, Dragonslayer. Try again.'"

    elif node == 212:
        context['game_mode'] = 'riddle'
        context['npc_name'] = 'Mysterious Bard'
        context['npc_image'] = 'bard.png'
        context['riddle_question'] = "\"Brilliant!\" The bard clapped and laughed. \n\n\"Second: It is always ahead of you, yet you can never catch it; but when it truly arrives, everything you are will come to an end.\""
        if request.session.pop('riddle_wrong', False):
            context['riddle_error'] = "The bard shakes his head. 'Wrong, Dragonslayer. Try again.'"

    elif node == 213:
        context['game_mode'] = 'riddle'
        context['npc_name'] = 'Mysterious Bard'
        context['npc_image'] = 'bard.png'
        context['riddle_question'] = "\"The last one, and the hardest.\" The bard suddenly leaned in, lowering his voice. \n\n\"What is it that you cannot see when you hold it, hurts the most when lost, yet is the sole bargaining chip you grip tightly on this one-way journey?\""
        if request.session.pop('riddle_wrong', False):
            context['riddle_error'] = "The bard shakes his head. 'Wrong, Dragonslayer. Try again.'"

    elif node == 214:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I paused. The desperate tears of the villagers and the resolute face of the captain flashed through my mind. I looked up, meeting his gaze directly: \"Hope.\"",
            "The bard looked at me deeply, suddenly dropping all his playful smiles. With solemn reverence, he reached into his coat and produced an egg covered in crimson veins. It radiated a scorching heat.",
            "\"Take it, Dragonslayer. This is a Phoenix chick.\" He pushed it toward me. \"When the dragon's flames threaten to consume you, it will save you from the inferno.\"\n\n<span style='color: green; font-weight: bold;'>[ ✨ SUCCESS: Phoenix Chick has joined your party! ]</span>",
            "In the tavern's guest room, I used a rough bar of soap and a basin of hot water to wash away the blood and grime. This rare peace allowed me a long-overdue, dreamless sleep, free from the roars of dragons.",
            "The next morning, a crowd gathered before the village's wooden gates. The villagers called my name, pressing coarse rations into my pack. The guard captain stood at the forefront.",
            "\"The road ahead... even I have never tread it,\" the captain gripped my forearm firmly. \"Remember that look in your eyes last night. Don't die to those monsters.\"",
            "I nodded and mounted my horse. Facing the crisp morning breeze, I didn't look back, riding straight into the depths of the Dragon's Valley."
        ]

    elif node == 215:
        context['game_mode'] = 'story'
        context['npc_name'] = 'Mysterious Bard'
        context['npc_image'] = 'bard.png'
        context['story_texts'] = [
            "The bard stopped strumming his lute, a profound sense of pity flashing in his cloudy eyes.",
            "\"What a pity. It seems you are not the one who can pierce through the mist.\" He sighed, fished a few coins from his coat, and tossed them onto the table. \"Take this money and buy yourself a good drink, Dragonslayer. This journey might be too heavy a burden for you.\"",
            "With that, he pulled down the brim of his hat, slung his battered lute over his shoulder, and walked out of the tavern without looking back, leaving me stunned in place.",
            "<span style='color: gold; font-weight: bold;'>[ 💰 The Bard looks at you with pity, leaves you 10 coins, and departs. ]</span>",
            "I silently gathered the coins and returned to the guest room, washing away the blood and grime. This rare peace allowed me a long-overdue, dreamless sleep, free from the roars of dragons.",
            "The next morning, bidding farewell to the enthusiastic villagers and the guard captain, I mounted my horse. Facing the crisp morning breeze, I didn't look back, riding straight into the depths of the Dragon's Valley."
        ]

    elif node == 22:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "In the tavern's guest room, I used a rough bar of soap and a basin of hot water to wash away the blood and grime, changing into mended underclothes. The inn was rustic, but sufficiently warm. This rare peace allowed me a long-overdue, dreamless sleep, free from the roars of dragons.<br><br>"
            "The next morning, a crowd gathered before the village's wooden gates. There was no grand honor guard, no extravagant farewell speeches. The villagers simply called my name, pressing coarse rations into my pack. The stark contrast between this scene and my departure from the Royal Capital felt almost unfamiliar.<br><br>"
            "The guard captain stood at the forefront, his son timidly hiding behind him, looking at me with absolute adoration.<br><br>"
            "\"The road ahead... even I have never tread it,\" the captain gripped my forearm firmly, as if passing on a silent strength. \"Remember that look in your eyes last night. Don't die to those monsters.\"<br><br>"
            "I nodded and mounted my horse. Facing the crisp morning breeze, I didn't look back, riding straight into the depths of the Dragon's Valley. The lingering scent of rum and soap clung to my collar, and all hesitation in my heart had utterly vanished."
        ]

    elif node == 23:
        context['game_mode'] = 'interactive_npc'
        context['npc_name'] = 'Lost Tourists'
        context['npc_image'] = 'hunter.png'
        context['npc_dialogue'] = (
            "Walking onto the main road, I spotted two men wielding hunting rifles standing by the roadside. As I drew closer, I noticed the rifle of one man bore the crest of antlers.\n\n"
            "I discreetly observed them from the corner of my eye. One stood tall and impeccably dressed in a tailored suit, his every movement exuding the elegant aura of nobility. The other was dressed much more casually, wearing a simple, relaxed outfit that reminded me of a research professor I once met in the Royal Library.\n\n"
            "\"Hello.\" I snapped back to reality, realizing the blonde man in the suit was greeting me. I looked up, catching his deep, pale-grey eyes. A polite smile rested on his face, yet I caught a flicker of silent reproach in his gaze—I realized he had noticed my secret scrutiny from the very beginning.\n\n"
            "His accent carried the lilt of a foreigner, yet his phrasing was impeccably elegant. \"We are tourists here. Could you point us to a resting inn?\" He looked at me patiently, completely devoid of the anxiety or urgency typical of lost travelers, radiating an eerie composure instead. I frowned..."
        )
        context['choices'] = [
            {'text': 'Point toward the village I came from', 'action': 'hunter_opt1'},
            {'text': '"Do I look like someone who knows the way?" (Roll eyes)', 'action': 'hunter_opt2'}
        ]

    elif node == 231:
        context['game_mode'] = 'story'
        context['npc_name'] = 'Lost Tourists'
        context['npc_image'] = 'hunter.png'
        context['story_texts'] = [
            "I never fancied myself a man of strict etiquette, but the stranger was overwhelmingly polite. Facing a pair of eyes that seemed capable of piercing through everything, I grew nervous for no reason, only to belatedly find my own reaction amusing. I bowed slightly, offering a standard knight's salute to both strangers.",
            "\"Follow this road to the very end, and turn the corner after you see the barn. You'll find an inn there,\" I described the route in detail, summarizing at the end.",
            "\"Thank you.\" The blonde man smiled at me gratefully. I noticed his lips part slightly, as if he hesitated to speak.",
            "The dark-haired man beside him was clearly much more introverted. As he tilted his head up to thank me, I finally caught a clear view of his face. He wore thick, black-rimmed glasses that perfectly complemented his slightly curly dark hair, completely fitting the image of a quiet researcher. He smiled at me and awkwardly returned a knight's salute, drawing a soft chuckle from the blonde man next to him.",
            "\"Thank you, Dragonslayer.\" He glanced sideways, glaring at the blonde man who had yet to suppress his amusement.",
            "\"You're welcome.\" I was startled. Was he an Arcanist capable of reading minds? How could he know I was a Dragonslayer just by looking at me? I was about to ask, but the blonde man beat me to it—",
            "\"We have little to offer in return. Perhaps you could leave us your knight's crest. Once we settle in, we might host a dinner party. If you would do us the honor of attending...\"",
            "His words were cut short as the dark-haired man abruptly coughed, walking away and striding down the path I had pointed out. The blonde man froze for a second before donning that impeccable smile once more. \"Apologies, Sir Knight. Perhaps we will have to wait for another opportunity to properly introduce ourselves.\"",
            "He quickened his pace to catch up with his companion, leaving me standing alone, lost in thought as I watched their retreating silhouettes."
        ]

    elif node == 232:
        context['game_mode'] = 'story'
        context['npc_name'] = 'Lost Tourists'
        context['npc_image'] = 'wendigo.png'
        if request.session.get('visited_village', False):
            smell_text = "Yet you clearly carry the lingering scent of rum mixed with soap." 
        else:
            smell_text = "Yet you clearly carry the stench of wild mud and rotten blood."   
        context['story_texts'] = [
            f"\"Is that so?\" The blond man wasn't angered by my impatient attitude. Instead, he narrowed his eyes. The lingering smile vanished, leaving only an emotionless, bottomless black, like inorganic glass beads. \"{smell_text}\"His tone was peaceful, yet cut straight to the bone.",
            "My lie exposed, anger born of embarrassment flared up. I shot back mockingly, \"Perhaps your nose deceived you. After all, only Royal Hounds possess a sense of smell that sharp.\"",
            "I met his eyes provocatively, only to find absolutely zero emotion on his face. *He is slowly savoring my emotions.* The sudden thought sprang into my mind, making all the hairs on my body stand on end. Even though I was gripping my weapon and clad in armor, I failed to instill even a sliver of fear in him. It felt as though I was the sinner who had made a fatal misstep.",
            "\"Dr. Lecter,\" the dark-haired man beside him suddenly spoke up, breaking the surging, dark tension. \"Let's go.\"",
            "\"Oh? Will, are we no longer using our first names?\" The blond man instantly switched to a gentle expression when facing him, a curve pulling at the corner of his lips. \"Give me just a moment, Will.\" His tone actually carried a hint of lamentation, reminding me of the gloomy atmosphere at a Royal Funeral, where the Grand Maester would mourn the late King in the exact same voice.",
            "Alarm bells screamed in my mind, but before I could even draw my weapon, Dr. Lecter moved faster.",
            "An atomizer aimed directly at my armor's breathing vent sprayed an unknown mist right into my nasal cavity. It burned and screamed, instantly hijacking my senses. In a split second, my hands lost all strength, drooping numbly at my sides. Dancing points of light flooded my vision. I dazedly reached out, only to feel cold steel.",
            "A scalpel.",
            "\"Etiquette is merely a thin layer of clothing wrapped around human skin,\" Dr. Lecter whispered softly. \"People judge beauty and gender by appearance; they express intimacy and friendly exchange by touching each other's skin.\"",
            "I couldn't comprehend his philosophies. My head spun violently, nearly bringing me to my knees. \"What did you do? Do you have any idea—\"",
            "\"Shh.\" Before my eyes, Dr. Lecter morphed through a myriad of human forms, finally transforming into a fallen god crowned with black antlers. The Wendigo of myth shed its skin of a perfect gentleman, smiling down at me. \"Let us see if your insides are as wretched as your outer skin, shall we?\"",
            "A flash of cold light, and immense agony erupted from my abdomen. I roared, trying to struggle, but Will was tightly locking my neck, as if I would suffocate to death if I made a single rash move. Countless thoughts flashed through my mind. In terror, I remembered the Puppeteer in the Royal Capital; his silver-tongued manipulation of his marionettes was identical to Dr. Lecter right now.",
            "Will cast a pitying glance at me, like the mercy of God.",
            "\"At least this hunt was not entirely fruitless.\" Right before I fell into a coma, I heard Dr. Lecter's voice. He was proudly displaying a bloody red object to his companion. \"If we can find—\"",
            "In my delirium, I heard fragmented syllables... words like 'ingredients' and 'dinner party'.<br><br><i>\"I seemed to see Love joyous<br>Allegro mi sembrava Amor<br>Holding my heart in his hand<br>Tenendo meo core in mano<br>And in his arms lay my love, sleeping, wrapped in a veil<br>E ne le braccia avea madoa involta in un drappo dormend.<br>Then he woke her, and she, trembling and submissive<br>Poi la svegliava, e d'esto core ardeo<br>Ate my burning heart from his hand<br>Lei paventoa umilmente pasc<br>I saw Love leave, his face bathed in tears...<br>appreso gir lo ne vedea piangendo\"</i>",
            "<span style='color: darkred; font-weight: bold;'>[ 🩸 WARNING: You were punished by Hannibal for your rudeness! HP reduced to 1! ]</span>"
        ]

    elif node == 24:
        context['game_mode'] = 'interactive_npc'
        context['npc_name'] = 'Pond Fairy'
        context['npc_image'] = 'fairy.png' 
        context['npc_dialogue'] = (
            "Passing through a dead forest that hadn't seen the sun in years, the surrounding miasma miraculously dissipated. Brushing aside the last thorny thicket, a crystal-clear spring appeared before me, with faintly glowing blue water lilies floating on the surface.\n\n"
            "An ethereal humming drifted from the water. As the mist cleared, a Fairy with transparent, delicate wings hovered in the center of the spring. Her face was unimaginably beautiful, and she looked at my scarred armor with a gaze full of pity.\n\n"
            "\"Brave soul, your journey is paved with thorns and blood.\" Her voice smoothed the agitation in my heart like clear water. The Fairy reached out a holy hand toward me. \"Will you accept the spring's blessing, let my light heal your wounds, and allow me to accompany you into the deepest darkness?\""
        )
        context['choices'] = [
            {'text': 'Refuse coldly: "I am used to being alone."', 'action': 'fairy_opt1'},
            {'text': 'Accept gratefully: "It would be my honor."', 'action': 'fairy_opt2'}
        ]

    elif node == 241:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I shook my head, gripping my sword tighter. \"The path of a dragonslayer is a solitary one. I cannot risk others getting hurt. Not even a sprite.\"",
            "The Fairy sighed softly, her glow dimming slightly. \"As you wish, proud knight. May the stars continue to guide your path.\"",
            "She dissolved into glowing motes of light and vanished into the spring, and the surroundings returned to a deathly silence."
        ]

    elif node == 242:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I dropped to one knee, hand over my heart, offering a devout knight's salute. \"It is my honor, gentle spirit. The darkness ahead is too thick; I am in dire need of a light to cleave through it.\"",
            "The Fairy blossomed into a warm smile. She fluttered her delicate wings, sprinkling shimmering stardust over my armor. A refreshing wave of vitality instantly surged through my veins, and my gruesome wounds healed and scabbed over at a visible rate.",
            "\"When you fall into the dark, I will kindle an inextinguishable light for you,\" she whispered softly, transforming into a sphere of soft, radiant light that quietly settled into my knapsack.",
            "<span style='color: green; font-weight: bold;'>[ ✨ SUCCESS: Fairy has joined your party! You recovered 20 HP. ]</span>"
        ]

    elif node == 25:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Bidding farewell to the Fairy, I gathered my gear by the strange, crystal-clear spring. Just as I stepped out of the dead woods, a man wrapped in a coarse gray cloak blocked my path. He was crouching on the ground, inspecting animal tracks, and stood up alertly at the sound of my footsteps. He looked travel-worn, his face slightly weathered beneath the hood, carrying the scent of moss and foliage from years of navigating the woods.",
            "\"The path ahead is blocked, Lord Knight.\" He clapped the dirt from his hands, his tone carrying the exhaustion of a wanderer. \"The main road was claimed by a pack of two-headed beasts for their nest last night. I am a ranger from the village, planning to detour. If you don't mind, I know a hidden trail that can bypass their sight entirely undetected.\"",
            "The soul in my mind let out a very faint, cold snort, seemingly scoffing at this sudden approach from a stranger."
        ]

    elif node == 251:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "The gray cloak led me deeper into uncharted terrain. The damp soil was gradually replaced by a bizarre, vibrant vegetation. Suddenly, the view opened up, and a dazzling, breathtaking sea of flowers stretched before me. The blossoms were monstrously huge, blooming in sickly shades of scarlet and violet. The sickeningly sweet, almost bitter floral scent rushed at me, nearly suffocating me in its heavy air.",
            "How could such beauty exist in this desolate, cursed land? For a moment, I was completely mesmerized.",
            "\"Fool.\" The soul's sharp rebuke exploded in my mind.",
            "In a flash, my intoxicated mind snapped awake. The texture of the supposedly soft floral carpet beneath my boots shifted instantly—it became viscous, slimy, carrying a malicious suction. I looked down in horror as the mirage before my eyes burned away like a scorched canvas. There was no sea of flowers. It was a putrid, stinking swamp."
        ]

    elif node == 26:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Mist choked the swamp. I stepped into a muddy hollow, and no matter how I struggled, I couldn't pull my trapped boot free. Just as frustration took hold, dormant vines silently coiled around my ankle. I tried to dispel them with an incantation, but it backfired; I was bound fast to the spot, entirely immobilized.<br><br>"
            "A light, melodic chuckle drifted closer through the gloom. I glared furiously at the dark wizard who materialized from the mist, but he ignored my silent protest. Stepping close, he brazenly looked me up and down.<br><br>"
            "\"Is all this truly worth it?\" he began, waving a hand to conjure a mirage before my eyes. In the illusion, the king was immersed in endless revelry, while the city guards slacked off in gluttony. He smiled faintly, tapping my temple. \"You are brave, but to come all this way for these people... it isn't worth it.\"<br><br>"
            "I froze. Those illusions took root and sprouted in my mind like magic beans, faintly shaking my unwavering resolve. Barely surviving countless brushes with death to get here—was it really worth it? But this seed of doubt did not last long. The faces of the companions I had met on this journey leaped vividly back into my mind, and the words they had spoken to me slowly filled my heart.<br><br>"
            "When I first embarked on this journey, I was fearful and cowardly. But now, I am no longer the person I used to be. Even if it isn't for anyone else, just to ensure this bitter trek wasn't made in vain, I must point my sword at the dragon and challenge it. Not to mention—<br><br>"
            "\"Where there are hedonists, there are strivers; where there are cowards, there are the brave. You cannot blind yourself to the pristine light worth admiring and protecting just because there is filth in the world.\" A cold scoff escaped my nose. \"Did you think I haven't questioned if it's worth it? I've asked myself countless times, and my answer has always been the exact same.\"<br><br>"
            "I lunged at the wizard. \"I only care about my true heart, and it tells me that all of this is worth it.\""
        ]

    elif node == 27:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="witch").first()
            if not enemy:
                enemy = EnemyType.objects.first()
            if enemy:
                active_encounter = Encounter.objects.create(player=player, enemy_type=enemy, enemy_hp=enemy.max_hp, status="ACTIVE")

    elif node == 28:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "With the dark wizard's body dissolving into a puddle of foul, viscous black sludge, the oppressive mist finally cleared.",
            "I leaned heavily against my sword, gasping for air as I forced my exhausted body to stay upright. Just then, the familiar scent of old parchment and wild grit wafted through the air. The merchant's lantern flickered at the edge of the mist, and he casually strolled to the edge of the devastated swamp.",
            "\"It seems you are far more resilient than I imagined, Dragonslayer,\" he said, assessing me with his usual calm demeanor. \"The wizard is dead. The shadow looming over the village has been cleared.\"",
            "\"The Dragon's Valley lies just ahead.\" I could almost smell the damp scent of the impending storm. \"I suppose this is where we part ways. Your 'kindred' can accompany me from here.\" I was referring to the soul that had been entrenched in my mind.",
            "The merchant paused, a profound confusion seeping from beneath his hood. \"Kindred? Sir Knight, my nose smells only the stench of blood and rotting mud. Aside from the dead, what other presence could there be?\"",
            "Suddenly, the soul in my mind, silent for so long, spoke up with extreme impatience. \"Stop wasting your breath on this coin-stinking mortal!\" His voice rattled my skull, carrying an unprecedented, oppressive urgency. \"Your destiny lies ahead! Draw your sword and sever that vile dragon's head!\"",
            "\"It wouldn't hurt to buy some supplies before I go,\" I muttered. Defeating the wizard had completely drained me. \"This might be our final trade.\"",
            "\"It won't be.\" The merchant unrolled his pack, patting my shoulder. \"We will meet again. Now, stock up, for what lies beyond is nightmares made flesh. \""
        ]

    elif node == 29:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Bidding farewell to the merchant, I embarked alone on the final stretch toward the Dragon's Valley. Along the way, I saw the 'signposts' left behind by my predecessors."
            "They were not signposts at all. They were rusted, shattered swords, cracked crests, and bleached bones half-buried in the volcanic ash. I realized then that I was not the only dragonslayer to reach this place. These skeletons were the remnants of beguiled minds, unfulfilled ambitions, and broken hopes."
        ]

    elif node == 291:
        context['game_mode'] = 'story'
        
        signposts = Signpost.objects.order_by('?')[:40]
        
        if signposts.exists():
            messages_text = "I crouched down and wiped the volcanic ash from the cracked stones. I could barely make out the bloodstained final words left by the predecessors:<br>"
            for sp in signposts:
                messages_text += f"<br><span style='color: #d3d3d3; font-style: italic;'>「 {sp.message} 」</span>"
        else:
            messages_text = "<span style='color: #8b8b83; font-style: italic;'>The wind and snow had completely erased any text on the stones. I could read nothing.</span>"

        context['story_texts'] = [
            messages_text
        ]

    elif node == 30:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "When I finally crested the peak and stepped onto the massive, dead altar, the thin air pressed down on me heavily—a suffocating oppression identical to the one in my nightmares. The heavens tore open, and from a deep, black vortex, a sky-blotting, ancient dragon crashed down, shattering the stone slabs beneath its feet.",
            "It did not immediately unleash its fiery breath. Instead, it lowered its terrifying, arrogant head and stared dead at me. In that instant, my blood ran cold. Those lifeless, pale-grey eyes... like glass beads. It was that inviolable, overwhelming presence, looking down at a mortal's futile struggle with utter apathy.",
            "\"You are finally here, my brave dragonslayer.\" A sharp spike seemed to pierce my brain. \"It has been so long since I've seen a fresh one.\"",
            "The dragon did not open its abyssal, fang-filled maw, yet those mocking, languid words exploded simultaneously within my mind and across the empty valley.",
            "My blood froze instantly; my mind went completely blank.",
            "The 'soul guide' who had accompanied me, directed me, mocked me, and even urged me to slay the beast just moments ago... was no wandering ghost at all. It was the abyssal dragon itself! It had been lurking in my consciousness the entire time, treating my desperate, agonizing trek like an amusing theatrical play performed by a mere ant!"
        ]

    elif node == 31:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="dragon").first()
            if not enemy:
                enemy = EnemyType.objects.first()
            if enemy:
                active_encounter = Encounter.objects.create(player=player, enemy_type=enemy, enemy_hp=enemy.max_hp, status="ACTIVE")

    elif node == 32:
        context['game_mode'] = 'interactive_npc'
        context['npc_name'] = 'Dying Abyssal Dragon'
        context['npc_image'] = 'dragon.png' 
        context['npc_dialogue'] = (
            "The colossal beast finally collapsed, its golden blood pooling over the shattered altar and scattering coins. The abyssal aura within its chest was fading, yet its pale-grey eyes still stared at me, devoid of fear, filled only with a chilling amusement.\n\n"
            "\"Well done... my brave puppet,\" the dragon rasped. Its voice echoed in my mind one last time, weaker now, but still dripping with mockery. \"You have danced beautifully to the very end.\"\n\n"
            "I stood before its massive corpse, feeling the suffocating dark power radiating from it. My blade trembled in my hands. \"Why? Why guide me all this way, just to let me kill you?\"\n\n"
            "\"Kill me?\" The dragon let out a low, gurgling chuckle that made my skin crawl. \"Energy never dies, Dragonslayer. It merely changes vessels. This was never a hunt... it was a succession ritual.\"\n\n"
            "It weakly shifted its massive head, presenting its glowing, corrupted eye to me. \"Now, look into my eye... claim the dark power you have rightfully earned. Or... are you too cowardly to embrace true godhood?\"\n\n"
            "The dragon drew its final breath, leaving behind a suffocating silence and an eye that pulsed with a beguiling, crimson glow. It is time to make my final decision."
        )
        context['choices'] = [
            {'text': 'Gouge out the dragon\'s eye and absorb the dark power.', 'action': 'ending_dragon'},
            {'text': 'Raise your staff and burn the corpse and bones to ashes.', 'action': 'ending_hero'}
        ]

    elif node == 33:
        context['game_mode'] = 'ending_signpost' 
        context['ending_type'] = 'Bad Ending'
        context['story_texts'] = [
            "As if possessed, I walked toward the dragon's corpse and reached out to gouge out the dark-gold dragon eye radiating a beguiling glow.<br><br>"
            "In an instant, a frenzied dark power surged through my veins. My skin began to sprout hard, dark-red scales; the bones in my back tore apart violently as a pair of sky-blotting fleshy wings burst from my flesh.",
            "Gazing down at the insignificant human capital, a deafening roar tore from my throat... The dragonslayer had ultimately become the next evil dragon to rule the world.<br><br><span style='color:darkred; font-weight:bold;'>【 BAD ENDING: Gaze of the Abyss 】</span><br><br>The cycle continues. Leave your dying words for the next Dragonslayer:"
        ]

    elif node == 34:
        context['game_mode'] = 'ending_signpost' 
        context['ending_type'] = 'True Ending'
        context['story_texts'] = [
            "Resisting the eerie temptation radiating from the dragon's eye, I raised my staff, channeled every last drop of my mana, and unleashed the most scorching fireball upon the dragon's corpse.<br><br>"
            "The raging inferno reduced the dragon's bones and its wicked curses to ashes. Sunlight finally pierced through the gloom that had shrouded the royal capital for years.",
            "I dragged my exhausted body back to the town. This time, there was no superficial honor guard—only the heartfelt cheers and warm tears of the reborn commoners... The spark of hope had finally been rekindled in this era.<br><br><span style='color:goldenrod; font-weight:bold;'>【 TRUE ENDING: Breaking Dawn 】</span><br><br>Your journey is over. Leave a message of guidance for the next Dragonslayer:"
        ]

    if context['game_mode'] == 'combat':
        if active_encounter:
            context['active_encounter'] = active_encounter
            if active_encounter.enemy_type.max_hp > 0:
                context['enemy_hp_percent'] = int((active_encounter.enemy_hp / active_encounter.enemy_type.max_hp) * 100)
        else:
            messages.error(request, "A disturbance in the magical weave occurred. The world has reset.")
            return redirect('/game/restart/')
    
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
        except json.JSONDecodeError:
            data = {}

        action_type = data.get("action_type", "fight")
        item_id = data.get("item_id")
        
        active_encounter = player.encounters.filter(status="ACTIVE").first()
        
        if not active_encounter:
            return JsonResponse({"error": "No active enemies around you!"}, status=400)

        enemy_type = active_encounter.enemy_type

        if enemy_type.name.upper() == "WITCH" and action_type == "magic":
            return JsonResponse({"error": "The dark wizard's shadow power suppresses your magic and makes it impossible to cast it!"}, status=400)

        player_damage = 0
        incoming_damage_reduction = 0
        enemy_damage = max(1, random.randint(max(1, enemy_type.damage - 2), enemy_type.damage + 2))

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
            if enemy_type.name.upper() != "DRAGON":
                player_damage = 0
                log_message = "🛡️ Your allies are saving their strength for the final battle. You must face this enemy alone!"
            else:
                active_friend = player.friends.filter(is_active=True).first()

                if not active_friend:
                    player_damage = 0
                    log_message = "🤝 You called out for help, but no one answered. You are completely alone... or your allies have already exhausted their strength."
                else:
                    player_damage = random.randint(5, 12)
                    heal_amount = random.randint(8, 16)
                    player.hp = min(100, player.hp + heal_amount)
                    
                    friend_name = active_friend.friend.name
                    
                    log_message = (
                        f"🤝 {friend_name} steps forward to fulfill the oath! They distract the {enemy_type.name} "
                        f"for {player_damage} damage, restore {heal_amount} of your HP, and then retreat exhausted!"
                    )
                    
                    active_friend.is_active = False
                    active_friend.save()

        elif action_type == "item":
            inventory_qs = player.inventory.select_related("item").filter(
                quantity__gt=0,
                item__type="CONSUMABLE",
            )

            if item_id:
                inventory_qs = inventory_qs.filter(item_id=item_id)

            inventory_item = inventory_qs.order_by("-item__effect_value", "item__name").first()
            if not inventory_item:
                return JsonResponse({"error": "You do not have any usable consumable item."}, status=400)

            item = inventory_item.item
            inventory_item.quantity -= 1
            if inventory_item.quantity > 0:
                inventory_item.save(update_fields=["quantity"])
            else:
                inventory_item.delete()

            if item.effect == "HEAL":
                heal_amount = item.effect_value
                player.hp = min(100, player.hp + heal_amount)
                log_message = f"🧪 You used {item.name} and recovered {heal_amount} HP!"
            elif item.effect == "DAMAGE_BOOST":
                player_damage = random.randint(8, 15) + item.effect_value
                log_message = f"🧪 You used {item.name} and struck for {player_damage} boosted damage!"
            elif item.effect == "DEFENCE_BOOST":
                incoming_damage_reduction = item.effect_value
                log_message = (
                    f"🧪 You used {item.name}. Incoming damage will be reduced by "
                    f"{incoming_damage_reduction} this turn."
                )
            else:
                log_message = f"🧪 You used {item.name}, but nothing happened."

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
            enemy_damage = max(0, enemy_damage - incoming_damage_reduction)
            player.hp -= enemy_damage
            if enemy_damage > 0:
                log_message += f"<br>The {enemy_type.name} hit you back for {enemy_damage} damage."
            else:
                log_message += f"<br>The {enemy_type.name}'s attack was fully blocked!"
            
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
    player.current_node = 0  
    player.monsters_defeated = 0

    player.save()
    player.encounters.all().delete()
    
    player.encounters.filter(status__in=["ACTIVE", "LOST"]).delete()
    
    player.friends.all().delete()
    return redirect('game:main')
