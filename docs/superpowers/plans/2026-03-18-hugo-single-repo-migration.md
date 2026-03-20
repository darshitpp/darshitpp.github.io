# Hugo Single-Repository Migration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate Hugo blog from two-repo setup to single `darshitpp.github.io` repository with GitHub Actions auto-deploy.

**Architecture:** Create `hugo` branch in `darshitpp.github.io` containing all Hugo source files, with GitHub Actions workflow that auto-deploys to `master` branch on every push.

**Tech Stack:** Hugo static site generator, GitHub Actions, peaceiris/actions-hugo@v3, peaceiris/actions-gh-pages@v4

---

## Chunk 1: Pre-Migration Safety Checks

### Task 0: Environment and Safety Verification

**Files:**
- Working directory: `/Users/darshit/Projects/blog`
- Working directory: `/Users/darshit/Projects/darshitpp.github.io`

- [ ] **Step 0a: Verify Hugo is installed locally**

```bash
which hugo && hugo version
```
Expected: Shows Hugo version (e.g., `hugo v0.140.0`)

If not installed: `brew install hugo`

- [ ] **Step 0b: Verify git connectivity to both remotes**

```bash
cd /Users/darshit/Projects/blog && git remote -v
cd /Users/darshit/Projects/darshitpp.github.io && git remote -v
git fetch --all 2>&1
```
Expected: Both repos show `origin` URLs, fetch succeeds

- [ ] **Step 0c: Verify both repos are clean (no uncommitted changes)**

```bash
cd /Users/darshit/Projects/blog && git status --porcelain
cd /Users/darshit/Projects/darshitpp.github.io && git status --porcelain
```
Expected: Empty output (no uncommitted changes)

If dirty: Commit or stash changes before proceeding

- [ ] **Step 0d: Verify both repos are synced with remote**

```bash
cd /Users/darshit/Projects/blog
git fetch origin
git status
# Should show "up to date" or "ahead/behind" info

cd /Users/darshit/Projects/darshitpp.github.io
git fetch origin
git status
```
Expected: Both repos show "up to date" or local ahead of remote (not behind)

- [ ] **Step 0e: Create backup branch on master (safety net)**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
git branch backup-pre-migration
git push origin backup-pre-migration
git branch -a | grep backup
```
Expected: `backup-pre-migration` branch created locally and on remote

- [ ] **Step 0f: Verify current live site is accessible**

```bash
curl -s -o /dev/null -w "%{http_code}" https://darshit.dev
```
Expected: `200` (site is live and accessible)

- [ ] **Step 0g: Verify CNAME file exists on master**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
git show master:CNAME
```
Expected: Shows `darshit.dev`

- [ ] **Step 0h: Save critical backup info to persistent location**

```bash
# Save to home directory (persists across sessions unlike /tmp)
cd /Users/darshit/Projects/darshitpp.github.io
git rev-parse HEAD > ~/hugo-migration-master-backup.txt
echo "$(date)" >> ~/hugo-migration-master-backup.txt
cat ~/hugo-migration-master-backup.txt
```
Expected: Shows backup SHA and timestamp

---

### Task 1: Create Backup of Current State

**Files:**
- Working directory: `/Users/darshit/Projects/blog`
- Working directory: `/Users/darshit/Projects/darshitpp.github.io`

- [ ] **Step 1: Commit blog repo cleanly**

```bash
cd /Users/darshit/Projects/blog
git status
git add -A
git commit -m "backup before migration to single-repo setup"
git log -1 --oneline
```
Expected: Clean commit showing backup state

- [ ] **Step 2: Commit github.io repo cleanly**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
git status
git add -A
git commit -m "backup before migration to single-repo setup"
git log -1 --oneline
```
Expected: Clean commit showing backup state

- [ ] **Step 3: Record current master commit SHA for rollback**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
git rev-parse HEAD > /tmp/master-backup-sha.txt
cat /tmp/master-backup-sha.txt
```
Expected: Prints commit SHA (e.g., `1de1372...`)

- [ ] **Step 4: Verify both repos are in sync with remote**

```bash
cd /Users/darshit/Projects/blog && git remote -v
cd /Users/darshit/Projects/darshitpp.github.io && git remote -v
```
Expected: Both show `origin` pointing to correct GitHub repos

---

### Task 2: Audit Files to Migrate

**Files:**
- Source: `/Users/darshit/Projects/blog/`
- Output: Migration checklist in terminal

- [ ] **Step 1: List all files in blog/ root**

```bash
cd /Users/darshit/Projects/blog
find . -maxdepth 1 -type f -not -name ".DS_Store" -not -name ".hugo_build.lock"
```
Expected: `config.yml`, `.gitmodules`, `deploy-website.sh`, etc.

- [ ] **Step 2: List content directory**

```bash
cd /Users/darshit/Projects/blog
find content/ -type f | head -20
```
Expected: List of `.md` files in `content/posts/`, `content/about.md`, etc.

- [ ] **Step 3: List themes directory**

```bash
cd /Users/darshit/Projects/blog
ls -la themes/
```
Expected: `hugo-PaperMod/` directory

- [ ] **Step 4: List static, layouts, archetypes**

```bash
cd /Users/darshit/Projects/blog
ls -la static/ layouts/ archetypes/ 2>/dev/null || echo "dir not found"
```
Expected: Contents of each directory

- [ ] **Step 5: Create migration exclusion list**

Files to EXCLUDE from migration:
- `public/` (generated output)
- `.gitmodules` (no submodules needed)
- `.git/` (fresh repo on target)
- `.hugo_build.lock` (build artifact)
- `.DS_Store` (macOS artifact)

---

## Chunk 2: Create Hugo Branch in darshitpp.github.io

### Task 3: Create Orphan Hugo Branch

**Files:**
- Working directory: `/Users/darshit/Projects/darshitpp.github.io`

- [ ] **Step 1: Navigate to github.io repo**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
pwd
```
Expected: `/Users/darshit/Projects/darshitpp.github.io`

- [ ] **Step 2: Create orphan hugo branch locally**

```bash
git checkout --orphan hugo
git status
```
Expected: On branch `hugo`, all files staged for commit

- [ ] **Step 3: Remove all files from staging (master untouched)**

```bash
git rm -rf .
git status
```
Expected: All files deleted from staging, `CNAME` and others show as deleted

- [ ] **Step 4: Verify master branch still exists**

```bash
git branch -a
git log master --oneline -1
```
Expected: Shows `master` branch with previous commit intact

- [ ] **Step 5: Copy Hugo source files from blog/ directory**

```bash
# From blog dir, copy everything except excluded files
cd /Users/darshit/Projects/blog
rsync -av --exclude='public/' --exclude='.git/' --exclude='.gitmodules' \
  --exclude='.hugo_build.lock' --exclude='.DS_Store' \
  ./ /Users/darshit/Projects/darshitpp.github.io/
```
Expected: All Hugo source files copied

- [ ] **Step 5a: Copy CNAME to static/ for Hugo to include in build**

```bash
# CNAME must be in static/ so Hugo copies it to public/
cd /Users/darshit/Projects/darshitpp.github.io
git show master:CNAME > static/CNAME
cat static/CNAME
```
Expected: Shows `darshit.dev`

- [ ] **Step 6: Verify copied files in github.io**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
ls -la
ls content/
ls themes/
```
Expected: Shows `content/`, `config.yml`, `themes/`, `static/`, etc.

- [ ] **Step 7: Add all files to git**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
git add -A
git status
```
Expected: All new files staged for commit on `hugo` branch

- [ ] **Step 8: Commit migration**

```bash
git commit -m "migrate hugo source from two-repo setup"
git log -1 --oneline
```
Expected: New commit on `hugo` branch

- [ ] **Step 8a: Pre-flight Hugo build test (CRITICAL)**

```bash
# Test build locally before pushing to GitHub
# Ensure Hugo is installed: brew install hugo
cd /Users/darshit/Projects/darshitpp.github.io
hugo --minify
echo "Build exit code: $?"
ls public/ | head -5
```
Expected: Build succeeds (exit code 0), shows `index.html`, `posts/`, etc.

- [ ] **Step 8b: Verify CNAME in build output**

```bash
# Confirm CNAME is in the build output
cat /Users/darshit/Projects/darshitpp.github.io/public/CNAME
```
Expected: Shows `darshit.dev`

- [ ] **Step 9: Push hugo branch to GitHub**

```bash
git push -u origin hugo
```
Expected: Branch `hugo` created on remote

- [ ] **Step 9a: Verify hugo branch exists on remote**

```bash
git fetch origin
git branch -r | grep hugo
```
Expected: Shows `origin/hugo`

- [ ] **Step 9b: Verify master branch is untouched**

```bash
git log origin/master --oneline -1
git rev-parse origin/master
```
Expected: Same commit SHA as before (unchanged from backup)

---

### Task 3a: Verify Local Build Before Actions (CRITICAL CHECKPOINT)

**Purpose:** Catch Hugo build issues BEFORE pushing to GitHub

- [ ] **Step 1: Run Hugo build locally**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
hugo --minify 2>&1
echo "Exit code: $?"
```
Expected: Build succeeds, exit code 0, no errors

- [ ] **Step 2: Verify build output exists**

```bash
ls -la public/ | head -10
```
Expected: Shows `index.html`, `posts/`, `categories/`, `tags/`, `sitemap.xml`

- [ ] **Step 3: Verify CNAME in build output**

```bash
cat public/CNAME
```
Expected: Shows `darshit.dev`

- [ ] **Step 4: Verify index.html exists and is valid**

```bash
head -20 public/index.html
```
Expected: Shows valid HTML with your site title

- [ ] **Step 5: Clean up local build (not needed in repo)**

```bash
rm -rf public/
git status
```
Expected: Clean working directory (no uncommitted changes)

**⚠️ CHECKPOINT:** If any step above fails, STOP and fix before proceeding. The GitHub Actions workflow will fail the same way.

---

---

### Task 4: Create Updated .gitignore

**Files:**
- Create: `/Users/darshit/Projects/darshitpp.github.io/.gitignore`

- [ ] **Step 1: Create Hugo-specific .gitignore**

```markdown
# Hugo
.DS_Store
.hugo_build.lock
public/
resources/

# macOS
.DS_Store

# Editor
*.swp
*.swo
*~
.idea/
.vscode/
```

- [ ] **Step 2: Write .gitignore file**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
cat > .gitignore << 'EOF'
# Hugo build artifacts
.hugo_build.lock
public/
resources/

# macOS
.DS_Store

# Editor
*.swp
*.swo
*~
.idea/
.vscode/
EOF
cat .gitignore
```
Expected: Displays .gitignore content

- [ ] **Step 3: Commit .gitignore**

```bash
git add .gitignore
git commit -m "add .gitignore for hugo build artifacts"
git push origin hugo
```
Expected: .gitignore committed and pushed

---

## Chunk 3: Add GitHub Actions Workflow

### Task 5: Create Deploy Workflow

**Files:**
- Create: `/Users/darshit/Projects/darshitpp.github.io/.github/workflows/deploy.yml`

- [ ] **Step 1: Create .github/workflows directory**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
mkdir -p .github/workflows
ls .github/
```
Expected: Shows `workflows/` directory

- [ ] **Step 2: Write deploy.yml workflow file**

```yaml
name: Deploy Hugo Site

on:
  push:
    branches: [hugo]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: hugo

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: '0.140.0'
          extended: true

      - name: Build
        run: hugo --minify

      - name: Deploy to master
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
          publish_branch: master
          keep_files: true
          force_orphan: true
```

- [ ] **Step 3: Write workflow file using cat**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy Hugo Site

on:
  push:
    branches: [hugo]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: hugo

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: '0.140.0'
          extended: true

      - name: Build
        run: hugo --minify

      - name: Deploy to master
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
          publish_branch: master
          keep_files: true
          force_orphan: true
EOF
cat .github/workflows/deploy.yml
```
Expected: Displays complete workflow YAML

- [ ] **Step 4: Commit and push workflow**

```bash
git add .github/workflows/deploy.yml
git commit -m "add github actions deploy workflow"
git push origin hugo
```
Expected: Workflow committed and pushed to `hugo` branch

---

## Chunk 4: Verify Deployment

### Task 6: Trigger and Monitor Actions

**Files:**
- Monitor: GitHub Actions tab at `https://github.com/darshitpp/darshitpp.github.io/actions`

- [ ] **Step 1: Push small test change to trigger workflow**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
echo "# Test deployment" >> content/about.md
git add content/about.md
git commit -m "test deployment trigger"
git push origin hugo
```
Expected: Push triggers GitHub Actions workflow

- [ ] **Step 2: Monitor Actions tab**

Open: `https://github.com/darshitpp/darshitpp.github.io/actions`
Expected: Workflow "Deploy Hugo Site" running (~30-60 seconds)

- [ ] **Step 3: Wait for workflow completion**

Check workflow status:
- Green checkmark = success
- Red X = failure (check logs)

Expected: Success status

- [ ] **Step 4: Verify master branch updated**

```bash
git fetch origin master
git log origin/master --oneline -3
```
Expected: New commit on `master` branch from Actions

- [ ] **Step 5: Verify site loads at darshit.dev**

Open: `https://darshit.dev`
Expected: Site loads with "test deployment" content visible

- [ ] **Step 6: Verify CNAME preserved**

```bash
# Check via curl
curl -I https://darshit.dev | head -5
```
Expected: HTTP 200, no redirect errors

- [ ] **Step 7: Revert test change**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
git revert HEAD --no-edit
git push origin hugo
```
Expected: Test change reverted, new deploy triggered

- [ ] **Step 8: Wait for second deployment**

Monitor: `https://github.com/darshitpp/darshitpp.github.io/actions`
Expected: Second workflow run completes successfully

- [ ] **Step 9: Verify site after revert**

```bash
curl -s https://darshit.dev | grep -o '<title>.*</title>'
```
Expected: Shows your site title (test change removed)

---

### Task 6a: Post-Deployment Safety Verification

**Purpose:** Confirm everything works before declaring success

- [ ] **Step 1: Verify backup branch exists**

```bash
git branch -r | grep backup-pre-migration
```
Expected: Shows `origin/backup-pre-migration`

- [ ] **Step 2: Verify you can rollback if needed**

```bash
# Simulate rollback (DO NOT PUSH)
git checkout backup-pre-migration
git log --oneline -1
git checkout hugo  # Return to hugo branch
```
Expected: Can switch to backup, see old state, return to hugo

- [ ] **Step 3: Verify fallback deploy script still exists**

```bash
ls -la ~/Projects/blog/deploy-website.sh
file ~/Projects/blog/deploy-website.sh
```
Expected: Script exists and is executable

- [ ] **Step 4: Document current state for reference**

```bash
echo "=== Migration Complete ===" >> ~/hugo-migration-master-backup.txt
echo "Date: $(date)" >> ~/hugo-migration-master-backup.txt
echo "Hugo branch: $(git rev-parse HEAD)" >> ~/hugo-migration-master-backup.txt
echo "Master branch: $(git rev-parse origin/master)" >> ~/hugo-migration-master-backup.txt
cat ~/hugo-migration-master-backup.txt
```
Expected: Shows migration complete with commit SHAs

---

---

## Chunk 5: Fallback Preservation

### Task 7: Document Fallback Procedure

**Files:**
- Modify: `/Users/darshit/Projects/darshitpp.github.io/README.md` (create if needed)

- [ ] **Step 1: Create README.md with fallback docs**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
cat > README.md << 'EOF'
# Darshit Patel's Blog

## Deployment

### Primary: GitHub Actions (hugo branch)

1. Make changes to content, config, etc.
2. `git add . && git commit -m "changes"`
3. `git push origin hugo`
4. GitHub Actions auto-deploys to master (~30 seconds)

### Fallback: Manual Deploy Script

If Actions fails, use the old two-repo deploy script:

```bash
# From ~/Projects/blog
./deploy-website.sh
```

### Rollback

To rollback a bad deploy:
1. Revert on hugo branch: `git revert HEAD && git push`
2. Or manually revert master commit via GitHub UI

## Branches

- `hugo`: Hugo source files (push here)
- `master`: Generated HTML (Actions updates this)
EOF
cat README.md
```
Expected: Displays README with deployment docs

- [ ] **Step 2: Commit README**

```bash
git add README.md
git commit -m "add deployment documentation"
git push origin hugo
```
Expected: README committed and pushed

- [ ] **Step 3: Verify old deploy script still works**

```bash
# Test fallback path exists
ls -la /Users/darshit/Projects/blog/deploy-website.sh
```
Expected: Script exists and is executable

---

## Chunk 6: Cleanup and Verification

### Task 8: Final Verification Checklist

**Files:**
- Verification commands

- [ ] **Step 1: Verify single repo workflow**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
git branch -a
```
Expected: Shows `hugo` and `master` branches

- [ ] **Step 2: Verify old repos untouched**

```bash
cd /Users/darshit/Projects/blog
git status
cd /Users/darshit/Projects/darshitpp.github.io
git status
```
Expected: Both clean, no uncommitted changes

- [ ] **Step 3: Verify darshit.dev resolves**

```bash
curl -s -o /dev/null -w "%{http_code}" https://darshit.dev
```
Expected: `200`

- [ ] **Step 4: Verify Actions workflow history**

Check: `https://github.com/darshitpp/darshitpp.github.io/actions`
Expected: All recent runs successful

- [ ] **Step 5: Document rollback SHA for safety**

```bash
cd /Users/darshit/Projects/darshitpp.github.io
echo "Pre-migration master SHA: $(cat /tmp/master-backup-sha.txt)"
```
Expected: Shows backup SHA from Task 1

---

### Task 9: Update Local Workflow

**Files:**
- Working directory: `~/Projects/darshitpp.github.io` (new primary)

- [ ] **Step 1: Update shell alias or cd习惯**

Add to `~/.zshrc`:
```bash
alias blog='cd ~/Projects/darshitpp.github.io'
```

- [ ] **Step 2: Remove old blog/ from active workflow**

```bash
# Optionally archive old blog repo reference
# DO NOT DELETE - keep as fallback
echo "Primary work directory: ~/Projects/darshitpp.github.io"
```

- [ ] **Step 3: Test new workflow**

```bash
cd ~/Projects/darshitpp.github.io
git pull origin hugo
# Make a small change
git add . && git commit -m "workflow test"
git push origin hugo
# Check Actions tab
```
Expected: End-to-end workflow works

---

## Success Criteria Checklist

After completing all tasks, verify:

### Critical Checks (Must Pass)
- [ ] Single repository (`darshitpp.github.io`) contains all Hugo source on `hugo` branch
- [ ] `hugo` branch exists on remote (`origin/hugo`)
- [ ] Push to `hugo` triggers GitHub Actions workflow
- [ ] Actions workflow completes successfully (green checkmark)
- [ ] `master` branch updated by Actions (check commit SHA changed)
- [ ] `darshit.dev` loads correctly (HTTP 200)
- [ ] CNAME works (no "Site not found" error)
- [ ] `public/CNAME` generated in build output

### Rollback Checks (Must Pass)
- [ ] `backup-pre-migration` branch exists on remote
- [ ] Backup SHA saved to `~/hugo-migration-master-backup.txt`
- [ ] Old deploy script exists at `~/Projects/blog/deploy-website.sh`
- [ ] Can checkout backup branch and return to hugo

### Functional Checks (Must Pass)
- [ ] New post workflow: `git push origin hugo` → site updates
- [ ] Revert workflow: `git revert HEAD` → site rolls back
- [ ] Local build: `hugo --minify` succeeds
- [ ] README.md contains deployment docs

### Optional Cleanup (After Success)
- [ ] Delete `backup-pre-migration` branch: `git push origin --delete backup-pre-migration`
- [ ] Archive old `blog/` repo reference (keep for fallback)

---

## Emergency Recovery Scenarios

### Scenario 1: Actions Workflow Never Triggers

**Symptoms:** Push to `hugo` branch doesn't trigger workflow
**Causes:**
- Workflow file syntax error
- Wrong branch trigger
- GitHub Actions disabled

**Recovery:**
```bash
# Check workflow file
cat .github/workflows/deploy.yml
# Verify branch name is 'hugo' (not 'main' or 'master')

# Check GitHub repo settings
# Settings > Actions > General > Ensure "Allow all actions" is selected

# Fallback: Use old deploy script
cd ~/Projects/blog && ./deploy-website.sh
```

### Scenario 2: Hugo Build Fails in Actions

**Symptoms:** Actions shows red X, logs show Hugo error
**Causes:**
- Hugo version mismatch
- Missing dependencies
- Theme error

**Recovery:**
```bash
# Fix on hugo branch
hugo --minify  # Test locally first
git add . && git commit -m "fix build error"
git push origin hugo

# If can't fix quickly, use fallback
cd ~/Projects/blog && ./deploy-website.sh
```

### Scenario 3: Site Shows 404 or "Site Not Found"

**Symptoms:** `darshit.dev` shows GitHub 404
**Causes:**
- CNAME missing from build
- GitHub Pages not configured for master branch
- DNS propagation delay

**Recovery:**
```bash
# Verify CNAME in build
git checkout hugo
cat static/CNAME  # Should show darshit.dev

# Rebuild and check
hugo --minify
cat public/CNAME  # Should show darshit.dev

# Check GitHub Pages settings
# Settings > Pages > Source: Deploy from branch > Branch: master

# For DNS propagation, wait 5-10 minutes
```

### Scenario 4: Actions Deploys to Wrong Branch

**Symptoms:** Site not updating, wrong branch has new commits
**Causes:**
- `publish_branch` not set to `master`

**Recovery:**
```bash
# Check workflow
grep "publish_branch" .github/workflows/deploy.yml
# Should show: publish_branch: master

# Fix and repush
git add .github/workflows/deploy.yml
git commit -m "fix deploy branch"
git push origin hugo
```

### Scenario 5: Need to Completely Undo Migration

**Symptoms:** Want to go back to two-repo setup
**Recovery:**
```bash
# 1. Restore master from backup
cd ~/Projects/darshitpp.github.io
git checkout master
git reset --hard $(cat ~/hugo-migration-master-backup.txt | head -1)
git push --force origin master

# 2. Delete hugo branch
git branch -D hugo
git push origin --delete hugo

# 3. Delete backup branch
git push origin --delete backup-pre-migration

# 4. Continue with old workflow
cd ~/Projects/blog
./deploy-website.sh
```

---

## Rollback Procedure (If Needed)

If migration fails at any point:

```bash
# 1. Switch to master first (if on hugo branch)
cd ~/Projects/darshitpp.github.io
git checkout master

# 2. Delete hugo branch
git branch -D hugo
git push origin --delete hugo

# 3. Restore master to pre-migration state
git reset --hard $(cat /tmp/master-backup-sha.txt)
git push --force origin master

# 4. Continue using old two-repo deploy script
cd ~/Projects/blog
./deploy-website.sh
```

---

## Post-Plan Review

After completing this plan, dispatch `spec-document-reviewer` subagent to verify:
1. All files migrated correctly
2. Actions workflow functional
3. Site live at darshit.dev
4. Fallback preserved
