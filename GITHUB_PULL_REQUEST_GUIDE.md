# 🔄 GitHub Pull Request Guide - Odoo Custom Addons

## Complete Step-by-Step Guide to Create a Pull Request

This guide will walk you through creating a Pull Request (PR) to integrate your custom addons into your Odoo server.

---

## 📋 UNDERSTANDING THE SETUP

### Current Structure:
1. **Custom Addons Repository**: `C:/Users/MJWil/odoo_custom_addons/`
   - Your custom modules (vendor_product_importer, etc.)
   - GitHub: https://github.com/MJWHLLC/odoo-custom-addons
   - Branch: `17.0`

2. **Odoo Server**: `C:/Program Files/Odoo 17.0.20250119/server/`
   - Official Odoo installation
   - Contains core Odoo files

### Configuration:
Your `odoo.conf` already points to your custom addons:
```
addons_path = c:\program files\odoo 17.0.20250119\server\odoo\addons,C:\Users\MJWil\odoo_custom_addons
```

---

## 🎯 SCENARIO 1: PULL REQUEST WITHIN YOUR CUSTOM ADDONS REPO

If you want to create a PR to merge changes between branches in your custom addons repository:

### Step 1: Check Current Branch Status
```bash
cd "C:/Users/MJWil/odoo_custom_addons"
git status
git branch -a
```

### Step 2: Create a Feature Branch (if needed)
```bash
# Create a new branch for your feature
git checkout -b feature/my-new-feature

# Make your changes, then commit
git add .
git commit -m "Add new feature description"
git push origin feature/my-new-feature
```

### Step 3: Create Pull Request on GitHub

**Option A: Using GitHub Web Interface**
1. Go to: https://github.com/MJWHLLC/odoo-custom-addons
2. Click "Pull requests" tab
3. Click "New pull request"
4. Select:
   - **Base branch**: `17.0` (the branch you want to merge INTO)
   - **Compare branch**: `feature/my-new-feature` (your feature branch)
5. Click "Create pull request"
6. Add title and description
7. Click "Create pull request"

**Option B: Using GitHub CLI (gh)**
```bash
cd "C:/Users/MJWil/odoo_custom_addons"

# Install GitHub CLI if not installed
# Download from: https://cli.github.com/

# Login to GitHub
gh auth login

# Create pull request
gh pr create --base 17.0 --head feature/my-new-feature --title "Add new feature" --body "Description of changes"
```

---

## 🎯 SCENARIO 2: PULL REQUEST FROM FORK TO ORIGINAL REPO

If you forked someone else's repository and want to contribute back:

### Step 1: Add Upstream Remote
```bash
cd "C:/Users/MJWil/odoo_custom_addons"

# Add the original repository as upstream
git remote add upstream https://github.com/ORIGINAL_OWNER/ORIGINAL_REPO.git

# Verify remotes
git remote -v
```

### Step 2: Sync with Upstream
```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream changes into your branch
git checkout 17.0
git merge upstream/17.0
```

### Step 3: Create Feature Branch
```bash
# Create feature branch
git checkout -b feature/my-contribution

# Make changes and commit
git add .
git commit -m "Description of contribution"
git push origin feature/my-contribution
```

### Step 4: Create Pull Request
1. Go to your fork: https://github.com/MJWHLLC/odoo-custom-addons
2. Click "Contribute" → "Open pull request"
3. GitHub will detect you want to merge to the upstream repository
4. Fill in PR details and submit

---

## 🎯 SCENARIO 3: INTEGRATING CUSTOM ADDONS INTO ODOO SERVER

If you want to integrate your custom addons directly into the Odoo server directory:

### ⚠️ WARNING
This is **NOT RECOMMENDED** because:
- Odoo server directory should remain clean
- Updates will overwrite your changes
- Better to use `addons_path` in `odoo.conf` (already configured!)

### Current Best Practice (Already Implemented):
Your `odoo.conf` already includes:
```
addons_path = c:\program files\odoo 17.0.20250119\server\odoo\addons,C:\Users\MJWil\odoo_custom_addons
```

This means Odoo automatically loads modules from both:
1. Official Odoo addons
2. Your custom addons directory

**No Pull Request needed!** Your modules are already integrated.

---

## 🚀 RECOMMENDED WORKFLOW

### For Development:

1. **Work in Custom Addons Directory**
   ```bash
   cd "C:/Users/MJWil/odoo_custom_addons"
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

3. **Make Changes**
   - Edit your module files
   - Test in Odoo

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

5. **Push to GitHub**
   ```bash
   git push origin feature/new-feature
   ```

6. **Create Pull Request**
   - Go to GitHub
   - Create PR from `feature/new-feature` to `17.0`
   - Review and merge

7. **Update Local Main Branch**
   ```bash
   git checkout 17.0
   git pull origin 17.0
   ```

8. **Restart Odoo**
   - Restart Odoo service to load changes
   - Or update module in Odoo Apps menu

---

## 📝 PULL REQUEST BEST PRACTICES

### PR Title Format:
```
[TYPE] Brief description

Examples:
[FEATURE] Add Amazon product import adapter
[FIX] Resolve price calculation bug
[DOCS] Update installation guide
[REFACTOR] Improve code structure
```

### PR Description Template:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- List specific changes
- Include file names if relevant

## Testing
- [ ] Tested on Odoo 17.0
- [ ] All existing tests pass
- [ ] Added new tests (if applicable)

## Screenshots (if applicable)
Add screenshots showing the changes

## Related Issues
Closes #123 (if applicable)
```

---

## 🔧 COMMON COMMANDS

### Check Status
```bash
cd "C:/Users/MJWil/odoo_custom_addons"
git status
git log --oneline -5
```

### View Branches
```bash
git branch -a
```

### Switch Branches
```bash
git checkout 17.0
git checkout feature/my-feature
```

### Update from Remote
```bash
git fetch origin
git pull origin 17.0
```

### View Remotes
```bash
git remote -v
```

### View Commit History
```bash
git log --graph --oneline --all
```

---

## 🌐 USING GITHUB WEB INTERFACE

### Step-by-Step:

1. **Navigate to Repository**
   - Go to: https://github.com/MJWHLLC/odoo-custom-addons

2. **Go to Pull Requests Tab**
   - Click "Pull requests" at the top

3. **Create New PR**
   - Click green "New pull request" button

4. **Select Branches**
   - **Base**: The branch you want to merge INTO (usually `17.0`)
   - **Compare**: Your feature branch

5. **Review Changes**
   - GitHub shows a diff of all changes
   - Review files changed

6. **Create PR**
   - Click "Create pull request"
   - Add title and description
   - Click "Create pull request" again

7. **Review Process**
   - You can add reviewers
   - Discuss changes in comments
   - Make additional commits if needed

8. **Merge PR**
   - Once approved, click "Merge pull request"
   - Choose merge method:
     - **Merge commit**: Keeps all commits
     - **Squash and merge**: Combines into one commit
     - **Rebase and merge**: Replays commits

---

## 🔄 SYNCING ODOO WITH YOUR CHANGES

After merging a PR, update Odoo:

### Method 1: Restart Odoo Service
```bash
# Stop Odoo
# (Use Windows Services or Task Manager)

# Start Odoo
# (Use Windows Services or run odoo-bin)
```

### Method 2: Update Module in Odoo
1. Log into Odoo
2. Go to Apps menu
3. Remove "Apps" filter
4. Search for your module
5. Click "Upgrade" button

### Method 3: Command Line Update
```bash
cd "C:/Program Files/Odoo 17.0.20250119/server"
python odoo-bin -c odoo.conf -u vendor_product_importer -d your_database_name
```

---

## 📊 CURRENT REPOSITORY STATUS

Your repository is already set up:
- ✅ GitHub repository: https://github.com/MJWHLLC/odoo-custom-addons
- ✅ Branch `17.0` exists and is pushed
- ✅ Branch `main` exists
- ✅ All files committed and pushed
- ✅ Odoo configured to use custom addons

---

## 🎯 QUICK START: CREATE YOUR FIRST PR

```bash
# 1. Navigate to your custom addons
cd "C:/Users/MJWil/odoo_custom_addons"

# 2. Create a new feature branch
git checkout -b feature/test-pr

# 3. Make a small change (example: update README)
echo "Test change" >> README.md

# 4. Commit the change
git add README.md
git commit -m "Test: Add test change to README"

# 5. Push to GitHub
git push origin feature/test-pr

# 6. Go to GitHub and create PR
# Visit: https://github.com/MJWHLLC/odoo-custom-addons/pulls
# Click "New pull request"
# Select base: 17.0, compare: feature/test-pr
# Create the PR
```

---

## 🆘 TROUBLESHOOTING

### Issue: "Permission denied"
**Solution**: Ensure you're logged into GitHub and have push access
```bash
git remote -v
# Should show your repository URL
```

### Issue: "Branch not found"
**Solution**: Push your branch first
```bash
git push origin your-branch-name
```

### Issue: "Merge conflicts"
**Solution**: Resolve conflicts locally
```bash
git checkout 17.0
git pull origin 17.0
git checkout your-feature-branch
git merge 17.0
# Resolve conflicts in files
git add .
git commit -m "Resolve merge conflicts"
git push origin your-feature-branch
```

---

## 📞 SUPPORT

**Repository**: https://github.com/MJWHLLC/odoo-custom-addons
**Your Email**: info@mj-wilkerson-holdings-llc.odoo.com

---

## ✅ SUMMARY

Your setup is already optimal:
- Custom addons in separate directory
- Odoo configured to load from custom directory
- GitHub repository set up and synced
- No PR needed for basic integration

**Use PRs for**:
- Merging feature branches
- Code review process
- Contributing to other repositories
- Team collaboration

**Your modules are already integrated with Odoo through `odoo.conf`!**
