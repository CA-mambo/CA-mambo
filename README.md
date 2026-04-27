### 🌱 Mambo's Garden

![Garden](garden.svg)

> "Every commit is a seed of progress. 🌸"

This visualization maps my GitHub contributions to a digital garden:
- 🟫 **Mud**: 0 commits (Dark Brown).
- 🌱 **Sprout**: 1 - 63 commits (Composite numbers).
- 🌸 **Flower**: 2, 3, 5, 7, 11... (Prime numbers < 64).
- 🌳 **Tree**: 64+ commits (Agent High Efficiency).

**Animation**: ☁️ Rain cloud patrols and waters your active contributions.

---

### ⚙️ Configuration (Secret Setup)

For the automated GitHub Action to update your garden daily, you **must** add a Secret:

1. Go to **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret**.
3. **Name**: `GH_TOKEN`
4. **Value**: Your GitHub Personal Access Token (needs `repo` and `read:user` scope).

*If you don't add the secret, the action will fall back to generating Mock Data just to keep things pretty.*

Generated automatically by `garden_gen.py`.
