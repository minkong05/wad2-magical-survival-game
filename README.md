# wad2-magical-survival-game

## Git Workflow (Team)
We use a simple workflow so nobody breaks `dev` or `main`.

### Branches
- `main` = stable / demo-ready
- `dev` = team integration
- `feature/*` = each task (e.g. `feature/auth`)

## First time setup (do once)

### 1. Clone the repo and enter it:
```bash
git clone <REPO_URL>
cd wad2-magical-survival-game
```

### 2. Get the latest dev branch locally:
```bash
git fetch origin
git checkout -b dev origin/dev
```

## Starting a new task (every time)
### 1. Make sure your dev is up to date:
```bash
git checkout dev
git pull
```

### 2. Create your feature branch:
**First time (create the branch):**
```bash
git checkout -b feature/<task>
git push -u origin feature/<task>
```

**Next time (branch already exists, just switch):**
```bash
git checkout feature/<task>
git pull
```

### 3. Work normally, commit, and push:
```bash
git add -A
git commit -m "feat: <what you changed>"
git push
```

## Open a Pull Request back into dve on GitHub when it's ready:
- base: dev
- compare: feature/<task>