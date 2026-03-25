from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from game.models import PlayerProfile, Item, InventoryItem, Encounter, EnemyType, FriendType, PlayerFriend
import json


class BaseGameTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="hero", password="pass123")
        self.profile = PlayerProfile.objects.create(
            user=self.user,
            hp=100,
            coins=0,
            monsters_defeated=0
        )
        self.client.login(username="hero", password="pass123")

class TestCharacterSelect(BaseGameTest):

    # The test_character_can_be_selected checks that submitting "SWORDSMAN" to the character‑select view correctly updates the player’s 
    # profile to mark the character as chosen and store "SWORDSMAN" as the selected character.
    def test_character_can_be_selected(self):
        response = self.client.post(reverse("game:character_select"), {"class_type": "SWORDSMAN"})
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.class_selected)
        self.assertEqual(self.profile.class_type, "SWORDSMAN")

    # The test_cannot_reselect_class verifies that a player who has already chosen a character is immediately redirected when trying to
    # access the character‑select page again.
    def test_cannot_reselect_class(self):
        self.profile.class_selected = True
        self.profile.save()
        response = self.client.get(reverse("game:character_select"))
        self.assertEqual(response.status_code, 302)

class TestShopAccess(BaseGameTest):

    # The test_cannot_access_shop_outside_merchant checks that player cannot access the shop when the merchant is not there. 
    def test_cannot_access_shop_outside_merchant(self):
        self.profile.current_node = 0
        self.profile.save()
        response = self.client.get(reverse("game:shop"))
        self.assertEqual(response.status_code, 302)

    # The test_can_access_shop_in_merchant checks that the shop can be accessed when the merchant is present.
    def test_can_access_shop_in_merchant(self):
        self.profile.current_node = 9
        self.profile.save()
        response = self.client.get(reverse("game:shop"))
        self.assertEqual(response.status_code, 200)


class TestBuyItem(BaseGameTest):

    def setUp(self):
        super().setUp()
        self.item = Item.objects.create(
            name="Sword",
            price=10,
            type="WEAPON",
            effect_value=5
        )
        self.profile.coins = 50
        self.profile.save()

    # The test_buy_item_success check that buying an item successfully adds it to the player’s bag.
    def test_buy_item_success(self):
        response = self.client.post(reverse("game:buy_item", args=[self.item.id]))
        self.assertEqual(response.status_code, 302)
        inv = InventoryItem.objects.get(player=self.profile, item=self.item)
        self.assertEqual(inv.quantity, 1)

    # The test_cannot_buy_without_enough_coins checks that if the player does not have coins they are not allowed to buy the item.
    def test_cannot_buy_without_enough_coins(self):
        self.profile.coins = 0
        self.profile.save()
        response = self.client.post(reverse("game:buy_item", args=[self.item.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(InventoryItem.objects.filter(player=self.profile).exists())

    # The test_cannot_buy_duplicate_weapon checks that the player is not allowed to buy weapons more than once.
    def test_cannot_buy_duplicate_weapon(self):
        InventoryItem.objects.create(player=self.profile, item=self.item, quantity=1)
        response = self.client.post(reverse("game:buy_item", args=[self.item.id]))
        self.assertEqual(response.status_code, 302)
        inv_count = InventoryItem.objects.filter(player=self.profile, item=self.item).count()
        self.assertEqual(inv_count, 1)

class TestCombatEngine(BaseGameTest):

    def setUp(self):
        super().setUp()
        self.enemy = EnemyType.objects.create(
            name="Goblin",
            max_hp=50,
            damage=5,
            reward_coins=10
        )
        self.encounter = Encounter.objects.create(
            player=self.profile,
            enemy_type=self.enemy,
            enemy_hp=50,
            status="ACTIVE"
        )

    def attach_encounter(self):
        session = self.client.session
        session["active_encounter_id"] = self.encounter.id
        session.save()

    def perform_attack(self, payload):
        self.attach_encounter()
        return self.client.post(
            reverse("game:api_attack"),
            data=json.dumps(payload),
            content_type="application/json"
        )

    # The test_basic_fight_attack checks that a standard fight action is processed correctly and it results in the enemy taking damage.”
    def test_basic_fight_attack(self):
        response = self.perform_attack({"action_type": "fight"})
        data = response.json()
        self.assertIn("player_hp", data)
        self.assertIn("enemy_hp_percent", data)
        self.assertIn("log_message", data)
        self.encounter.refresh_from_db()
        self.assertLess(self.encounter.enemy_hp, 50)

    # The test_item_consumption checks that the item reducued its quantity in the bag after the player has used it.
    def test_item_consumption(self):
        potion = Item.objects.create(
            name="Potion",
            type="CONSUMABLE",
            effect="HEAL",
            effect_value=20,
            price=5
        )
        InventoryItem.objects.create(player=self.profile, item=potion, quantity=1)
        response = self.perform_attack({"action_type": "item", "item_id": potion.id})
        data = response.json()
        self.assertEqual(data["remaining_qty"], 0)
        self.assertEqual(data["used_item_name"], "Potion")

    # The test_enemy_can_kill_player checks that an enemy attack can reduce the player’s HP to zero and correctly mark the 
    # game as lost.
    def test_enemy_can_kill_player(self):
        self.profile.hp = 1
        self.profile.save()

        response = self.perform_attack({"action_type": "fight"})
        data = response.json()

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.hp, 0)
        self.assertEqual(data["game_status"], "lost")


class TestRestartGame(BaseGameTest):
   
   # The test_player_can_restart_game checks that the player can successfully restart the game.
   def test_player_can_restart_game(self):
    response = self.client.get(reverse("game:restart_game"))
    self.assertEqual(response.status_code, 302)
