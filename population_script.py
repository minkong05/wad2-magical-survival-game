import os
import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from game.models import EnemyType, Item, FriendType

    enemies = [
        # name, level, max_hp, damage, reward_coins, is_boss
        ("Skull", 1, 30, 6, 20, False),
        ("Zombie", 2, 45, 8, 40, False),
        ("Witch", 3, 85, 12, 60, False),
        ("Dragon", 4, 120, 18, 100, True),
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
        print(f"EnemyType: {obj.name} ({'created' if created else 'updated'})")

    items = [
        # name, type, price, effect, effect_value
        ("Sword", "WEAPON", 30, "DAMAGE_BOOST", 3),
        ("Armour", "ARMOUR", 25, "DEFENCE_BOOST", 3),
        ("HP Drink", "CONSUMABLE", 10, "HEAL", 20),
        ("Phoenix Food", "CONSUMABLE", 15, "HEAL", 35),
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
        print(f"Item: {obj.name} ({'created' if created else 'updated'})")
        
    friends = [
        # name, ability, effect_type, effect_value
        ("Phoenix", "Revive/heal support.", "HEAL", 25),
        ("Shooter", "Extra ranged damage.", "DAMAGE", 3),
        ("Fairy", "Boosts magic/spell power.", "SPELL", 2),
        ("Hulk", "Increases defence/toughness.", "DEFENCE", 3),
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
        print(f"FriendType: {obj.name} ({'created' if created else 'updated'})")

    print("Population script complete.")


if __name__ == "__main__":
    main()