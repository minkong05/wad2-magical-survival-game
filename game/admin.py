# game/admin.py
from django.contrib import admin
from .models import EnemyType, Item, FriendType
from .models import PlayerProfile, InventoryItem, PlayerFriend, Encounter


admin.site.register(Item)
admin.site.register(FriendType)

admin.site.register(PlayerProfile)
admin.site.register(InventoryItem)
admin.site.register(PlayerFriend)
admin.site.register(Encounter)


@admin.register(EnemyType)
class EnemyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "max_hp", "damage", "reward_coins", "is_boss")
    list_filter = ("level", "is_boss")
    search_fields = ("name",)
    ordering = ("level", "name")