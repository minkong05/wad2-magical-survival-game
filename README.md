# wad2-magical-survival-game

## Git Workflow (Team)

**Branches**
- `main` = stable / demo-ready
- `dev` = team integration
- `feature/*` = each task (e.g. `feature/login`)

**Repo owner (once)**
```bash
git checkout main && git pull
git checkout -b dev
git push -u origin dev
```

**Everyone (once)**
```bash
git fetch origin
git checkout -b dev origin/dev
```

**Daily**
```bash
git checkout dev && git pull
git checkout feature/<task>
# work...
git add . && git commit -m "feat: <msg>"
git push -u origin feature/<task>
```