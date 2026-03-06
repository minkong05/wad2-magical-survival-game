# Usage Guide (Dev)
How to run the project locally and use the current features.

## Run the project
**1) Activate venv + install deps**

```bash
source .venv/bin/activate
```

**2) Migrate DB**

```bash
python manage.py migrate
```
**3) Seed default game data (enemies/items/friends)**

```bash
python manage.py seed
```
**4) Start server**

```bash
python manage.py runserver
```
Open: http://127.0.0.1:8000/


## Admin (optional)
Create admin user:

```bash
python manage.py createsuperuser
```
