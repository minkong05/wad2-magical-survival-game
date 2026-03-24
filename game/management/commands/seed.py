# game/management/commands/seed.py
from django.core.management.base import BaseCommand
from game.models import EnemyType, Item, FriendType


class Command(BaseCommand):
    help = "Seed the database with default game data (enemies, items, friends)."

    def handle(self, *args, **options):
        self.seed_enemies()
        self.seed_items()
        self.seed_friends()
        self.stdout.write(self.style.SUCCESS("Seed complete."))

    def seed_enemies(self):
        enemies = [
            # name, level, max_hp, damage, reward_coins, is_boss
            (EnemyType.Name.SKULL, 1, 20, 2, 5, False),
            (EnemyType.Name.ZOMBIE, 2, 35, 4, 10, False),
            (EnemyType.Name.WITCH, 3, 50, 6, 20, False),
            (EnemyType.Name.DRAGON, 4, 120, 12, 100, True),
        ]

        for name, level, max_hp, damage, reward_coins, is_boss in enemies:
            obj, created = EnemyType.objects.update_or_create(
                name=name,
                defaults={
                    "level": level,
                    "max_hp": max_hp,
                    "damage": damage,
                    "reward_coins": reward_coins,
                    "is_boss": is_boss,
                },
            )
            self.stdout.write(f"EnemyType: {obj.get_name_display()} ({'created' if created else 'updated'})")

    def seed_items(self):
        items = [
            # name, type, price, effect, effect_value
            (Item.Name.SWORD, Item.Type.WEAPON, 30, Item.Effect.DAMAGE_BOOST, 3),
            (Item.Name.ARMOUR, Item.Type.ARMOUR, 25, Item.Effect.DEFENCE_BOOST, 3),
            (Item.Name.HP_DRINK, Item.Type.CONSUMABLE, 10, Item.Effect.HEAL, 20),
            (Item.Name.PHOENIX_FOOD, Item.Type.CONSUMABLE, 15, Item.Effect.HEAL, 35),
        ]

        for name, type_, price, effect, effect_value in items:
            obj, created = Item.objects.update_or_create(
                name=name,
                defaults={
                    "type": type_,
                    "price": price,
                    "effect": effect,
                    "effect_value": effect_value,
                },
            )
            self.stdout.write(f"Item: {obj.get_name_display()} ({'created' if created else 'updated'})")

    def seed_friends(self):
        friends = [
            # name, ability, effect_type, effect_value
            (FriendType.Name.PHOENIX, "Revive/heal support.", FriendType.EffectType.HEAL, 25),
            (FriendType.Name.SHOOTER, "Extra ranged damage.", FriendType.EffectType.DAMAGE, 3),
            (FriendType.Name.FAIRY, "Boosts magic/spell power.", FriendType.EffectType.SPELL, 2),
            (FriendType.Name.HULK, "Increases defence/toughness.", FriendType.EffectType.DEFENCE, 3),
        ]

        for name, ability, effect_type, effect_value in friends:
            obj, created = FriendType.objects.update_or_create(
                name=name,
                defaults={
                    "ability": ability,
                    "effect_type": effect_type,
                    "effect_value": effect_value,
                },
            )
            self.stdout.write(f"FriendType: {obj.get_name_display()} ({'created' if created else 'updated'})")