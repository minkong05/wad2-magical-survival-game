# Magical Survival Game — Game + Database + Features (Draft)

This document describes the **game logic**, **data model**, and **functional requirements** for the Magical Survival Game.  
(UI styling/graphics/wireframes are out of scope for this doc.)

---

## 1) Game Summary

Magical Survival Game is a browser-based fantasy RPG where players explore a magical world and fight increasingly dangerous enemies. Players choose a character class (Mage or Swordsman) and use a mix of standard combat, magic, and items to survive encounters across multiple levels—from early enemies such as Skulls to the final boss, the Dragon. Players earn coins from exploration and battles, can recruit helpful Friends/NPCs, and can buy equipment and consumables from the Shop. Player progress is saved to their account. The game is won when the Dragon is defeated.

---

## 2) Core Gameplay Loop (MVP)

1. **Authenticate**: User registers/logs in.
2. **Choose Class**: Mage or Swordsman (saved).
3. **Explore**: Trigger an encounter and/or earn rewards.
4. **Combat**: Use Attack / Magic / Item to resolve encounter.
5. **Rewards**: Gain coins and progress after victories/missions.
6. **Shop**: Spend coins on items and upgrades.
7. **Friends/NPCs**: Recruit friends that provide benefits.
8. Repeat until **Dragon defeated** → win.

---

## 3) Functional Requirements (Game Features)

### Authentication & Access
- Users **must** be able to create an account and log in before accessing game pages.
- Users **must** be able to log out at any time from the main game area.

### Player Progress
- Users **should** be able to track progress (e.g., coins earned, monsters defeated, current level).
- Player progress **must** be saved to their account.

### Combat
- Users **must** be able to perform standard attacks during combat.
- Users **must** be able to use magic skills during combat (Mage-focused).
- Users **may** use items during combat (e.g., healing potion/HP drink).

### Levels / Enemies
- Users **must** be able to battle enemies across **4 difficulty levels**:
  - Level 1: Skulls
  - Level 2: Zombies
  - Level 3: Witches
  - Level 4: Dragons
- Defeating the Dragon **wins the game**.

### Coins / Economy
- Users **must** be able to earn coins by defeating enemies, completing missions, and exploring.
- Users **must** be able to visit a Shop and spend coins on:
  - swords
  - HP drinks
  - phoenix food
  - armour

### Friends / NPCs
- Users **must** be able to recruit Friends:
  - Phoenix
  - Shooter
  - Fairy
  - Hulk
- Each Friend provides a unique ability (e.g., healing, extra damage, spell effect, etc.).

---

## 4) Database Design (Draft ER / Models)

We separate **per-user state** (changes per player) from **shared game definitions** (same for everyone).

### 4.1 Per-user entities

#### PlayerProfile (per user)
Stores the persistent player state.
- `user` (OneToOne → Django User)
- `class_type` (Mage/Swordsman)
- `level` (int)
- `hp` (int)
- `coins` (int)
- `monsters_defeated` (int, optional)

#### InventoryItem (per user)
Stores what items a player owns.
- `player` (ForeignKey → PlayerProfile)
- `item` (ForeignKey → Item)
- `quantity` (int)

#### PlayerFriend (per user)
Stores which friends have been recruited.
- `player` (ForeignKey → PlayerProfile)
- `friend` (ForeignKey → FriendType)
- `is_active` (bool, optional)
- `unlocked_at` (datetime, optional)

#### Encounter (optional; can be session-based for MVP)
Represents an active combat encounter.
- `player` (ForeignKey → PlayerProfile)
- `enemy_type` (ForeignKey → EnemyType)
- `enemy_hp` (int)
- `status` (active/won/lost)

> MVP simplification: Encounter can be stored in `request.session` instead of a model.

---

### 4.2 Shared (seeded) entities

These are the same for every dev machine and should be created using a **seed/population script** (do not share `db.sqlite3`).

#### EnemyType
Defines enemy stats and rewards.
- `name` (Skull/Zombie/Witch/Dragon)
- `level` (1–4)
- `max_hp` (int)
- `damage` (int)
- `reward_coins` (int)
- `is_boss` (bool)

#### Item
Defines shop items and item effects.
- `name` (Sword, Armour, HP Drink, Phoenix Food)
- `type` (weapon/armour/consumable)
- `price` (int)
- `effect` (string or enum; e.g., heal, damage_boost)
- `effect_value` (int, optional)

#### FriendType
Defines recruitable friends and abilities.
- `name` (Phoenix/Shooter/Fairy/Hulk)
- `ability` (string; description)
- `effect_type` (heal/damage/spell/defence)
- `effect_value` (int, optional)

#### Skill (optional)
If implementing a skill system beyond basic actions.
- `name`
- `damage` / `heal`
- `cost` / `cooldown` (optional)

---

## 5) Data Initialisation (Seed / Population)

To keep development consistent across teammates:

- Database schema is shared via **migrations** (committed to git).
- Default game data is shared via a **seed/population command**, e.g.:
  - EnemyType: Skulls, Zombies, Witches, Dragon
  - Item: Sword, Armour, HP Drink, Phoenix Food
  - FriendType: Phoenix, Shooter, Fairy, Hulk