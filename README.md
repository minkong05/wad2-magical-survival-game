# ⚔️ Magical Survival Game

*A dark-fantasy survival RPG web adventure built with Django*

*Originally served as the group project for Web App Development 2, University of Glasgow (Lab Group 6, Team B)*

## 👥 Authors

* [@minkong05](https://github.com/minkong05) (Yu Kong Yu Min - 3037931K)
* [Marchharee](https://github.com/Marchharee)(Yuxuan Song - 3075515S)
* [AIN340](https://github.com/AIN340)(Aman Iqbal Noreen - 2897234I)
* [Isaac2391](https://github.com/Isaac2391)Isaac Wilson (2961656W)
* [toluda17](https://github.com/toluda17)Toluwani David Ashiru (2925102D)

---

## ✨ Game Features

### 👤 User System
* **Secure Authentication:** Registration, secure login, and logout functionality.
* **Persistent Player Profiles:** * Real-time tracking of HP, Coins, and Monsters Defeated.
  * Dynamic Inventory management (Weapons, Armour, Consumables).
* **Death Penalty System:** Rogue-like punishment clears inventory and deducts coins upon death to ensure a hardcore survival experience.

### ⚔️ Combat & Progression
* **Turn-Based Encounters:** Engage with various enemies (Skulls, Zombies, Witches) and face the ultimate Dragon Boss.
* **Strategic Resource Management:** * Limited Magic: Magic spells are restricted to **only 3 uses per entire game run**, requiring careful tactical planning.
  * Companion System: Recruit allies (Phoenix, Shooter, Fairy, Hulk) with unique passive buffs (Heal, Damage, Spell, Defence).
* **Merchant Shop:** Spend hard-earned coins to purchase vital supplies (HP Drinks, Phoenix Food) and equipment upgrades.**Shop will only be opened when the player meet the merchant, please pay attention when you meet the merchant**.

### 📖 Interactive Narrative
* **Branching Storylines:** Text-based exploration with crucial decision-making nodes that alter the outcome.
* **Riddle System:** Encounter the Mysterious Bard. Answer correctly to unlock the legendary Phoenix; fail, and face permanent consequences.
* **Asynchronous Multiplayer (Signpost System):** Upon reaching the endgame, players can engrave a permanent message on a signpost, leaving a legacy or hints for future players to discover.

### ⚙️ Tech Stack & Technical Highlights

* **Backend:** Python & Django (Robust database relations linking Users, Encounters, Items, and Story Nodes)
* **Frontend:** HTML, CSS, JavaScript (Including strict anti-cheat mechanisms preventing browser "Back" button exploits)
* **UI Framework:** Bootstrap 5 (Responsive Design for elegant, pixel-art themed interfaces)
* **Async API:** AJAX (Fetch API) & JSON (For seamless dynamic UI updates and state management)
* **Database:** SQLite3
* **Deployment:** PythonAnywhere
* **Testing:** Comprehensive unit test coverage (`game/tests.py`) ensuring game logic reliability

---

## 🚀 Demo

Play the live version here: **[https://marchhare.pythonanywhere.com](https://marchhare.pythonanywhere.com)**

---

## 📷 Screenshot
![1856bf8ef3e936f2ed7e4a24e5d4e7df](https://github.com/user-attachments/assets/566cbe64-0990-4b2d-b1d0-f8b2c6f67794)
![51fa30d6c901e741e876dab371c3544d](https://github.com/user-attachments/assets/48e90f60-8245-405a-a56e-eab49420c52b)
![c3db336c2c4cd1cbb768c13416bd3b2d](https://github.com/user-attachments/assets/f0fb2602-a469-44b4-83b7-0a7506dd28dd)
![20f329df8f603503fe5a1ae347879f58](https://github.com/user-attachments/assets/fa5ac270-3a6a-43bc-ae5c-d144b52b4fe9)
![74822b265855d57a3621e8f22cd1a4e1](https://github.com/user-attachments/assets/d2fc8376-b92f-4393-b670-3fd714a1d96a)
![6714e54e29066456e15f76d761535df4](https://github.com/user-attachments/assets/3250c27b-49f5-4534-a2db-3d45368b3d31)









---

## 💻 Run Locally

To run this game on your local machine, follow these steps:

```bash
# Clone the repository
git clone [https://github.com/minkong05/wad2-magical-survival-game.git](https://github.com/minkong05/wad2-magical-survival-game.git)

# Navigate to the project folder
cd wad2-magical-survival-game

# Set up virtual environment
python -m venv venv  # use python3 if doesn't work

# Activate environment
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# ------IMPORTANT------
# Run the database migrations
python manage.py makemigrations
python manage.py migrate

# Run the population script to load monsters, items, and friends
python population_script.py

# Start the server
python manage.py runserver

```


Access the game at: http://127.0.0.1:8000/

---

## 🎨 About Arts & External Resources
To comply with academic integrity, we acknowledge the following external resources:

Visual Assets (Pixel Art): The character, enemy, and NPC sprites were sourced from free-to-use assets on OpenGameArt.org and some of them are painted by our team member March Hare.

UI Framework: Bootstrap v5.3.2 for responsive grid layouts.

Storyline & World-building: All core narratives, NPC dialogues, and riddles are 100% original, written and designed by our team member March Hare.

---

## 🙏 Special Thanks
To those who supported the development of this project, played our early buggy builds, and helped us balance the dark-fantasy difficulty:

* iloveneosoulindeed

* Law

* Butterfly

* Mr.Unicorn

* December

* Lin

* AIN

* Scatlett

* wikry
