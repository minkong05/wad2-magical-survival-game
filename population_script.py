import os
import django

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from game.models import EnemyType, Item, FriendType

    # ---- Enemies ----
    enemies = [
        # name, level, max_hp, damage, reward_coins, is_boss
        ("SKULL", 1, 20, 2, 5, False),
        ("ZOMBIE", 2, 35, 4, 10, False),
        ("WITCH", 3, 50, 6, 20, False),
        ("DRAGON", 4, 120, 12, 100, True),
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
        print(f"EnemyType: {obj.get_name_display()} ({'created' if created else 'updated'})")

    # ---- Items ----
    items = [
        # name, type, price, effect, effect_value
        ("SWORD", "WEAPON", 30, "DAMAGE_BOOST", 3),
        ("ARMOUR", "ARMOUR", 25, "DEFENCE_BOOST", 3),
        ("HP_DRINK", "CONSUMABLE", 10, "HEAL", 20),
        ("PHOENIX_FOOD", "CONSUMABLE", 15, "HEAL", 35),
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
        print(f"Item: {obj.get_name_display()} ({'created' if created else 'updated'})")

    # ---- Friends ----
    friends = [
        # name, ability, effect_type, effect_value
        ("PHOENIX", "Revive/heal support.", "HEAL", 25),
        ("SHOOTER", "Extra ranged damage.", "DAMAGE", 3),
        ("FAIRY", "Boosts magic/spell power.", "SPELL", 2),
        ("HULK", "Increases defence/toughness.", "DEFENCE", 3),
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
        print(f"FriendType: {obj.get_name_display()} ({'created' if created else 'updated'})")

    print("Population script complete.")

if __name__ == "__main__":
    main()