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
            if player.current_node in [141, 142]:
                player.current_node = 15
                player.save()
                return redirect('game:main')
            elif player.current_node in [91, 92]:
                player.current_node = 10
                player.save()
                return redirect('game:main')
            elif player.current_node in [181, 182]:
                player.current_node = 19
                player.save()
                return redirect('game:main')
            elif player.current_node in [201, 202]:
                player.current_node = 21
                player.save()
                return redirect('game:main')
            elif player.current_node >= 30:
                return redirect('/game/restart/') 
            else:
                player.current_node += 1
                player.save()
                return redirect('game:main')
                
        elif action == "ending_dragon":
            player.current_node = 29  
            player.save()
            return redirect('game:main')
            
        elif action == "ending_hero":
            player.current_node = 30  
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

        elif action == "riddle_correct":
            player.current_node = 141 
            player.coins += 50 
            player.save()
            return redirect('game:main')
            
        elif action == "riddle_wrong":
            player.current_node = 142 
            player.save()
            return redirect('game:main')

        elif action == "hunter_opt1":
            player.current_node = 181
            player.save()
            return redirect('game:main')

        elif action == "hunter_opt2":
            player.current_node = 182
            player.hp = 1 
            player.save()
            return redirect('game:main')

        elif action == "giant_opt1":
            player.current_node = 91
            player.hp = max(1, player.hp - 20)
            player.save()
            return redirect('game:main')

        elif action == "giant_opt2":
            player.current_node = 92
            player.save()
            return redirect('game:main')

        elif action == "fairy_opt1":
            player.current_node = 201
            player.save()
            return redirect('game:main')

        elif action == "fairy_opt2":
            player.current_node = 202
            player.hp = min(player.hp + 30, 100)
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
            "Through the rain, a dim lantern suddenly lit up. A short, old man wrapped in a heavy cloak and carrying a massive pack appeared out of nowhere under a nearby tree."
        ]

    elif node == 9:
        context['game_mode'] = 'interactive_npc'
        context['npc_name'] = 'Angry Green Giant (Hulk)'
        context['npc_image'] = 'hulk.png' 
        context['npc_dialogue'] = (
            "Following the massive footprints in the mud, I stumbled upon a towering, green-skinned giant sitting on a fallen redwood. "
            "His muscles bulged like boulders, and his stomach let out a thunderous growl. He looked incredibly angry and hungry.\n\n"
            "Noticing my approach, he hoisted a massive boulder effortlessly and roared, 'Hulk smash! Leave Hulk alone!'"
        )
        context['choices'] = [
            {'text': 'Draw your sword: "I am a Dragonslayer, I fear no one!"', 'action': 'giant_opt1'},
            {'text': 'Lower weapon and offer rations: "You look starving. Have some food."', 'action': 'giant_opt2'}
        ]

    elif node == 91:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I drew my sword, ready to face this behemoth. But before I could even chant a spell, the green giant let out a deafening roar and smashed the ground with his fists.",
            "The shockwave sent me flying, crashing heavily into a tree trunk. Coughing up blood, I watched as the giant leaped into the sky and disappeared into the clouds.",
            "<span style='color: darkred; font-weight: bold;'>[ 💥 WARNING: Hulk smashed! You lost 20 HP! ]</span>"
        ]

    elif node == 92:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I slowly lowered my sword, pulled out the dried meat and bread from my knapsack, and tossed them to the giant.",
            "The green behemoth sniffed the food cautiously before devouring it in one massive bite. The furious glint in his eyes softened, replaced by a childlike satisfaction.",
            "\"Puny knight is good. Hulk likes puny knight,\" he grunted, pounding his massive chest. \"Hulk will help puny knight smash the winged lizard!\"",
            "<span style='color: green; font-weight: bold;'>[ 🤝 SUCCESS: Hulk has joined your party! You can now call upon his strength using the 'Friend' button in battles! ]</span>"
        ]

    elif node == 10:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I bid farewell to the mysterious merchant and stepped onto the muddy path once more.<br><br>"
            "The rain gradually stopped. I followed the desolate trail and arrived at a ruined farm. A shivering farmer stood before it, clutching a chipped pitchfork. Tears mixed with mud as he pleaded with me, crying that his son had been dragged away by a monster roaming nearby."
        ]

    elif node == 11:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "A crow outside the barn let out a sudden shriek. I snapped back to reality, my eyes locked on a rotting hand thrusting out from the ruined, withered blossoms. I tightened my grip on my weapon, bracing for the fight. Having accepted the plea of the unarmed and defenseless, I could not afford to show a sliver of cowardice."
        ]

    elif node == 12:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="ZOMBIE").first()
            if not enemy:
                enemy = EnemyType.objects.first() 
            if enemy:
                active_encounter = Encounter.objects.create(player=player, enemy_type=enemy, enemy_hp=enemy.max_hp, status="ACTIVE")

    elif node == 13:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "This zombie was far stronger than the skeleton from before. It reeked of nauseating rot, and every swipe carried a lethal force. I nimbly rolled to dodge its heavy blow and pierced its chest with a backhand thrust. Black blood spewed out as the massive body crashed to the ground.<br><br>"
            "Just as I was about to breathe a sigh of relief, a bone-chilling sound of skeletal restructuring came from behind. The corpse that should have been dead twitched bizarrely. Dragging its mangled half-body, the rotting flesh around its wound healed halfway, and it lunged at me again with an inhuman roar!<br><br>"
            "\"Damn it, it's not dead yet!\" I gritted my teeth and raised my sword without hesitation. This time, I gave it my all, directly severing its head, completely ending the agony of this walking corpse."
        ]

    elif node == 14:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "\"Thank you, Sir Knight... This road is filled with curses and despair, but the light in your heart will surely cleave through the darkness. Please, you must bravely carry on!\"<br><br>"
            "The farmer's gratitude turned into a few silver coins added to my knapsack. At the crossroad leaving the farm, I unexpectedly ran into the lantern-bearing merchant again.<br><br>"
            "\"Looks like you took down a big one, didn't you?\" The merchant smiled, laying out his wares."
        ]

    elif node == 15:
        context['game_mode'] = 'npc'
        context['npc_name'] = 'Mysterious Wandering Merchant'
        context['npc_image'] = 'merchant.png'
        context['npc_dialogue'] = (
            "My wares are at your disposal, Dragonslayer. Need anything? "
            "(Click 'SHOP' in the top right to trade, then press Enter to leave)"
        )

    elif node == 16:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "As my journey deepened, I discovered that this cursed land was not solely inhabited by monsters. Passing through a misty forest, I encountered a bard wearing a tall hat sitting on a tree stump. He insisted on having me guess a riddle.<br><br>"
            "\"What is something you possess but cannot see, and pains you most to lose?\"<br><br>"
            "\"Hope,\" I answered without hesitation.<br><br>"
            "After I correctly answered his tricky riddles, he laughed heartily and pulled a crimson egg from his coat, tossing it to me. \"Well done! This Phoenix chick will be your most loyal companion. Don't be fooled by its current state as an egg; its flames can dispel any gloom.\""
        ]

    elif node == 17:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "(The story of the Hunter unfolds here...)"
        ]

    elif node == 18:
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

    elif node == 181:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I never fancied myself a man of strict etiquette, but the stranger was overwhelmingly polite. Facing a pair of eyes that seemed capable of piercing through everything, I grew nervous for no reason, only to belatedly find my own reaction amusing. I bowed slightly, offering a standard knight's salute to both strangers.",
            "\"Follow this road to the very end, and turn the corner after you see the barn. You'll find an inn there,\" I described the route in detail, summarizing at the end.",
            "\"Thank you.\" The blonde man smiled at me gratefully. I noticed his lips part slightly, as if he hesitated to speak.",
            "The dark-haired man beside him was clearly much more introverted. As he tilted his head up to thank me, I finally caught a clear view of his face. He wore thick, black-rimmed glasses that perfectly complemented his slightly curly dark hair, completely fitting the image of a quiet researcher. He smiled at me and awkwardly returned a knight's salute, drawing a soft chuckle from the blonde man next to him.",
            "\"Thank you, Dragonslayer.\" He glanced sideways, glaring at the blonde man who had yet to suppress his amusement.",
            "\"You're welcome.\" I was startled. Was he an Arcanist capable of reading minds? How could he know I was a Dragonslayer just by looking at me? I was about to ask, but the blonde man beat me to it—",
            "\"We have little to offer in return. Perhaps you could leave us your knight's crest. Once we settle in, we might host a dinner party. If you would do us the honor of attending...\"",
            "His words were cut short as the dark-haired man abruptly walked away, striding down the path I had pointed out. The blonde man froze for a second before donning that impeccable smile once more. \"Apologies, Sir Knight. Perhaps we will have to wait for another opportunity to properly introduce ourselves.\"",
            "He quickened his pace to catch up with his companion, leaving me standing alone, lost in thought as I watched their retreating silhouettes."
        ]



    elif node == 182:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "\"Do I look like someone who knows the way around this cursed land?\" I scoffed and rolled my eyes impatiently.",
            "The blond man's polite smile didn't fade; instead, it deepened into something deeply unsettling. His eyes turned cold, observing me not as a warrior, but like a piece of exquisite meat on a butcher's block.",
            "\"How rude...\" he whispered softly.",
            "Before I could even reach for my sword, a silver scalpel flashed in his hand with terrifying speed. A searing pain erupted in my abdomen. I collapsed to my knees, blood pouring from the wound.",
            "He wiped his blade clean with a pristine handkerchief, looking down at me with absolute elegance. \"I am Hannibal Lecter. Consider this a lesson in table manners, Dragonslayer.\"",
            "He stepped over my gasping body and walked away into the mist.",
            "<span style='color: darkred; font-weight: bold;'>[ 🩸 WARNING: You were punished by Hannibal for your rudeness! HP reduced to 1! ]</span>"
        ]

    elif node == 19:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Next, by an abandoned wizard tower deep in the forest, a white-bearded old mage blocked my path. He inspected the longsword I had just sharpened and shook his head: \"Empty swordplay won't kill a dragon, child.\"<br><br>"
            "He tapped my forehead with his bony finger. In an instant, a scorching warmth flooded my veins. \"I'll teach you the 'Fireball' spell. Combined with your sword, it's enough to burn those fire-fearing monsters to ashes.\""
        ]

    elif node == 20:
        context['game_mode'] = 'interactive_npc'
        context['npc_name'] = 'Pond Fairy'
        context['npc_image'] = 'fairy.png'
        context['npc_dialogue'] = (
            "Deep within a serene glade, the fog parted to reveal a crystal-clear pond. "
            "A Fairy with iridescent wings hovered above the water, looking at my blood-stained armor with pity.\n\n"
            "\"Brave soul, your journey is paved with thorns. Will you allow my light to mend your wounds and accompany you into the dark?\""
        )
        context['choices'] = [
            {'text': 'Refuse coldly: "I work alone."', 'action': 'fairy_opt1'},
            {'text': 'Accept gratefully: "I would be honored, gentle spirit."', 'action': 'fairy_opt2'}
        ]

    elif node == 201:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I shook my head, gripping my sword tighter. \"The path of a dragonslayer is a solitary one. I cannot risk others getting hurt.\"",
            "The Fairy sighed softly, her glow dimming slightly. \"As you wish, proud knight. May the stars watch over you.\"",
            "She dissolved into glowing motes of light and vanished into the pond, leaving me alone once more."
        ]

    elif node == 202:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "I bowed respectfully. \"I would be honored, gentle spirit. The darkness ahead is too thick for one man to pierce alone.\"",
            "The Fairy smiled warmly, her voice like tinkling bells. She sprinkled glowing stardust over my armor. A refreshing energy surged through my body, immediately mending my bruised flesh and bones.",
            "\"I shall lend you my magic when you need it most,\" she whispered, transforming into a tiny orb of light that nestled into my knapsack.",
            "<span style='color: green; font-weight: bold;'>[ ✨ SUCCESS: Fairy has joined your party! You recovered 30 HP. You can summon her healing magic using the 'Friend' button! ]</span>"
        ]

    elif node == 21:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Bidding farewell to the mage, I met a man in a grey cloak at the forest's exit. He claimed to be a local guide who knew a shortcut to avoid large monster lairs. Having met so many friendly faces along the way, my tensed nerves relaxed slightly, and I followed him without suspicion.<br><br>"
            "He led me through a dazzling, breathtaking sea of flowers. The overwhelming fragrance almost drowned me. However, just as I was mesmerized by this rare beauty, the ground beneath my feet felt wrong. The illusion faded like ripples on water. There was no sea of flowers."
        ]

    elif node == 22:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Thick mist veiled the swamp. I stepped into a muddy hollow, and no matter how hard I struggled, I couldn't pull my trapped boot free. Just as frustration took hold, dormant vines silently coiled around my ankle. I tried to dispel them with an incantation, but it backfired; I was bound fast to the spot, entirely immobilized.<br><br>"
            "A light, melodic chuckle drifted closer through the gloom. I glared furiously at the dark wizard who materialized from the mist, but he ignored my silent protest. Stepping close, he brazenly looked me up and down.<br><br>"
            "\"Is all this truly worth it?\" he began, waving a hand to conjure a mirage before my eyes. In the illusion, the king was immersed in endless revelry, while the city guards slacked off in gluttony. He smiled faintly, tapping my temple. \"You are brave, but to come all this way for these people... it isn't worth it.\"<br><br>"
            "I froze. Those illusions took root and sprouted in my mind like magic beans, faintly shaking my unwavering resolve. Barely surviving countless brushes with death to get here—was it really worth it? But this seed of doubt did not last long. The faces of the companions I had met on this journey leaped vividly back into my mind, and the words they had spoken to me slowly filled my heart.<br><br>"
            "When I first embarked on this journey, I was fearful and cowardly. But now, I am no longer the person I used to be. Even if it isn't for anyone else, just to ensure this bitter trek wasn't made in vain, I must point my sword at the dragon and challenge it. Not to mention—<br><br>"
            "\"Where there are hedonists, there are strivers; where there are cowards, there are the brave. You cannot blind yourself to the pristine light worth admiring and protecting just because there is filth in the world.\" A cold scoff escaped my nose. \"Did you think I haven't questioned if it's worth it? I've asked myself countless times, and my answer has always been the exact same.\"<br><br>"
            "I lunged at the wizard. \"I only care about my true heart, and it tells me that all of this is worth it.\""
        ]

    elif node == 23:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="witch").first()
            if not enemy:
                enemy = EnemyType.objects.first()
            if enemy:
                active_encounter = Encounter.objects.create(player=player, enemy_type=enemy, enemy_hp=enemy.max_hp, status="ACTIVE")

    elif node == 24:
        context['game_mode'] = 'npc'
        context['npc_name'] = 'Merchant (Final Stop)'
        context['npc_image'] = 'merchant.png'
        context['npc_dialogue'] = (
            "This is it, Dragonslayer. I can go no further. Stock up now, for what lies beyond this door is nightmares made flesh. May fortune favor you. "
            "(Click 'SHOP' in the top right to trade"
        )


    elif node == 25:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "(Seeing the signposts and warnings left behind by previous players... The final destination is near.)"
        ]

    elif node == 26:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "The shattered signpost bore the final, desperate words carved by a previous hero, as a biting wind howled through the hall.<br><br>"
            "I tightened my grip on the hilt of my sword, stepped over a sea of bleached bones, and pushed open the massive bronze doors.<br><br>"
            "Coiled upon the throne sat the sky-blotting, pureblood red dragon. It slowly opened its dark-gold slitted pupils, eyeing me—its uninvited guest—with mocking amusement. The air was thick with the stench of sulfur and despair. The final trial had begun!"
        ]

    elif node == 27:
        context['game_mode'] = 'combat'
        if not active_encounter:
            enemy = EnemyType.objects.filter(name__iexact="dragon").first()
            if not enemy:
                enemy = EnemyType.objects.first()
            if enemy:
                active_encounter = Encounter.objects.create(player=player, enemy_type=enemy, enemy_hp=enemy.max_hp, status="ACTIVE")

    elif node == 28:
        context['game_mode'] = 'decision'  

    elif node == 29:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "As if possessed, I walked toward the dragon's corpse and reached out to gouge out the dark-gold dragon eye radiating a beguiling glow.<br><br>"
            "In an instant, a frenzied dark power surged through my veins. My skin began to sprout hard, dark-red scales; the bones in my back tore apart violently as a pair of sky-blotting fleshy wings burst from my flesh.",
            "Gazing down at the insignificant human capital, a deafening roar tore from my throat... The dragonslayer had ultimately become the next evil dragon to rule the world.<br><br><span style='color:darkred; font-weight:bold;'>【 BAD ENDING: Gaze of the Abyss 】</span><br><br>(Press Enter to restart)"
        ]

    elif node == 30:
        context['game_mode'] = 'story'
        context['story_texts'] = [
            "Resisting the eerie temptation radiating from the dragon's eye, I raised my staff, channeled every last drop of my mana, and unleashed the most scorching fireball upon the dragon's corpse.<br><br>"
            "The raging inferno reduced the dragon's bones and its wicked curses to ashes. Sunlight finally pierced through the gloom that had shrouded the royal capital for years.",
            "I dragged my exhausted body back to the town. This time, there was no superficial honor guard—only the heartfelt cheers and warm tears of the reborn commoners... The spark of hope had finally been rekindled in this era.<br><br><span style='color:goldenrod; font-weight:bold;'>【 TRUE ENDING: Breaking Dawn 】</span><br><br>(Press Enter to restart)"
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
