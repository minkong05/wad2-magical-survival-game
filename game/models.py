from django.conf import settings
from django.db import models

class PlayerProfile(models.Model):
    CLASS_CHOICES = (
        ("MAGE", "Mage"),
        ("SWORDSMAN", "Swordsman"),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class_type = models.CharField(max_length=20, choices=CLASS_CHOICES, blank=True, default="MAGE")
    class_selected = models.BooleanField(default=False)
    level = models.PositiveSmallIntegerField(default=1)
    hp = models.PositiveIntegerField(default=100)
    coins = models.PositiveIntegerField(default=0)
    monsters_defeated = models.PositiveIntegerField(default=0)

    current_node = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} ({self.class_type or 'No class'})"


class EnemyType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    level = models.PositiveSmallIntegerField(default=1)
    max_hp = models.PositiveIntegerField(default=20)
    damage = models.PositiveIntegerField(default=1)
    reward_coins = models.PositiveIntegerField(default=0)
    is_boss = models.BooleanField(default=False)
    
    can_revive = models.BooleanField(default=False)
    drops_item = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True, blank=True, related_name='dropped_by')

    def __str__(self):
        return self.name


class FriendType(models.Model):
    EFFECT_CHOICES = (
        ("HEAL", "Heal"),
        ("DAMAGE", "Damage"),
        ("SPELL", "Spell"),
        ("DEFENCE", "Defence"),
    )

    name = models.CharField(max_length=50, unique=True)
    ability = models.CharField(max_length=200, blank=True, default="")
    effect_type = models.CharField(max_length=20, choices=EFFECT_CHOICES)
    effect_value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Item(models.Model):
    TYPE_CHOICES = (
        ("WEAPON", "Weapon"),
        ("ARMOUR", "Armour"),
        ("CONSUMABLE", "Consumable"),
    )

    EFFECT_CHOICES = (
        ("HEAL", "Heal"),
        ("DAMAGE_BOOST", "Damage Boost"),
        ("DEFENCE_BOOST", "Defence Boost"),
    )

    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price = models.PositiveIntegerField(default=0)
    effect = models.CharField(max_length=20, choices=EFFECT_CHOICES)
    effect_value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


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
    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("WON", "Won"),
        ("LOST", "Lost"),
    )

    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="encounters")
    enemy_type = models.ForeignKey(EnemyType, on_delete=models.CASCADE)
    enemy_hp = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username} vs {self.enemy_type.name} ({self.status})"

class Signpost(models.Model):
    message = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    ending_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"[{self.ending_type}] {self.message}"

