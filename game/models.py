from django.conf import settings
from django.db import models


class PlayerProfile(models.Model):
    class ClassType(models.TextChoices):
        MAGE = "MAGE", "Mage"
        SWORDSMAN = "SWORDSMAN", "Swordsman"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class_type = models.CharField(max_length=20, choices=ClassType.choices, blank=True, default="")
    level = models.PositiveSmallIntegerField(default=1)
    hp = models.PositiveIntegerField(default=100)
    coins = models.PositiveIntegerField(default=0)
    monsters_defeated = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} ({self.class_type or 'No class'})"


class EnemyType(models.Model):
    class Name(models.TextChoices):
        SKULL = "SKULL", "Skull"
        ZOMBIE = "ZOMBIE", "Zombie"
        WITCH = "WITCH", "Witch"
        DRAGON = "DRAGON", "Dragon"

    name = models.CharField(max_length=20, choices=Name.choices, unique=True)
    level = models.PositiveSmallIntegerField(default=1)
    max_hp = models.PositiveIntegerField(default=20)
    damage = models.PositiveIntegerField(default=1)
    reward_coins = models.PositiveIntegerField(default=0)
    is_boss = models.BooleanField(default=False)

    def __str__(self):
        return self.get_name_display()


class FriendType(models.Model):
    class Name(models.TextChoices):
        PHOENIX = "PHOENIX", "Phoenix"
        SHOOTER = "SHOOTER", "Shooter"
        FAIRY = "FAIRY", "Fairy"
        HULK = "HULK", "Hulk"

    class EffectType(models.TextChoices):
        HEAL = "HEAL", "Heal"
        DAMAGE = "DAMAGE", "Damage"
        SPELL = "SPELL", "Spell"
        DEFENCE = "DEFENCE", "Defence"

    name = models.CharField(max_length=20, choices=Name.choices, unique=True)
    ability = models.CharField(max_length=200, blank=True, default="")
    effect_type = models.CharField(max_length=20, choices=EffectType.choices)
    effect_value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.get_name_display()


class Item(models.Model):
    class Name(models.TextChoices):
        SWORD = "SWORD", "Sword"
        ARMOUR = "ARMOUR", "Armour"
        HP_DRINK = "HP_DRINK", "HP Drink"
        PHOENIX_FOOD = "PHOENIX_FOOD", "Phoenix Food"

    class Type(models.TextChoices):
        WEAPON = "WEAPON", "Weapon"
        ARMOUR = "ARMOUR", "Armour"
        CONSUMABLE = "CONSUMABLE", "Consumable"

    class Effect(models.TextChoices):
        HEAL = "HEAL", "Heal"
        DAMAGE_BOOST = "DAMAGE_BOOST", "Damage Boost"
        DEFENCE_BOOST = "DEFENCE_BOOST", "Defence Boost"

    name = models.CharField(max_length=30, choices=Name.choices, unique=True)
    type = models.CharField(max_length=20, choices=Type.choices)
    price = models.PositiveIntegerField(default=0)
    effect = models.CharField(max_length=20, choices=Effect.choices)
    effect_value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.get_name_display()


class InventoryItem(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="inventory")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("player", "item")

    def __str__(self):
        return f"{self.player.user.username} - {self.item.name} x{self.quantity}"


class PlayerFriend(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="friends")
    friend = models.ForeignKey(FriendType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("player", "friend")

    def __str__(self):
        return f"{self.player.user.username} - {self.friend.name}"


class Encounter(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        WON = "WON", "Won"
        LOST = "LOST", "Lost"

    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="encounters")
    enemy_type = models.ForeignKey(EnemyType, on_delete=models.CASCADE)
    enemy_hp = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username} vs {self.enemy_type.name} ({self.status})"