# Hugo Single-Repository Deployment Design

**Date:** 2026-03-18
**Status:** Approved
**Author:** Darshit Patel

## Problem Statement

Current setup requires maintaining two separate repositories:
- `/Users/darshit/Projects/blog` - Hugo source files
- `/Users/darshit/Projects/darshitpp.github.io` - GitHub Pages destination

Deployment uses a manual shell script (`deploy-website.sh`) that:
1. Runs `hugo` build
2. Commits to blog repo
3. Commits to github.io repo
4. Pushes both separately

**Issues:**
- Two repositories to sync and maintain
- Duplicated git operations in deploy script
- Submodule complexity (`public/` points to github.io)
- Manual branch management if using submodules

## Goals

1. **Single repository** - all content and deployment in `darshitpp.github.io`
2. **Single deploy command** - `git push origin hugo` triggers auto-deploy
3. **No branch switching** - developer never manually switches branches
4. **Custom domain preserved** - `darshit.dev` continues working
5. **Rollback safety** - can revert to previous state at any time
6. **Fallback option** - old deploy script preserved as backup

## Non-Goals

- CI/CD platform migration (stay on GitHub Actions)
- Theme changes or redesign
- Content restructuring
- URL structure changes

## Architecture

### Target Structure

```
darshitpp.github.io/
├── .github/
│   └── workflows/
│       └── deploy.yml          # Auto-deploys on push to 'hugo' branch
├── content/                    # Migrated from blog/content/
├── config.yml                  # Migrated from blog/config.yml
├── themes/                     # Migrated from blog/themes/
├── static/                     # Migrated from blog/static/
├── layouts/                    # Migrated from blog/layouts/
├── archetypes/                 # Migrated from blog/archetypes/
├── .gitignore                  # Hugo build artifacts
└── CNAME                       # Preserved (darshit.dev)

Branches:
- hugo    : Hugo source files (developer pushes here)
- master  : Generated HTML (GitHub Actions updates this)
```

### Deployment Flow

```
Developer → git push origin hugo
    ↓
GitHub Actions (deploy.yml)
    ↓
1. Checkout hugo branch
2. Setup Hugo (extended, latest)
3. Run hugo --minify
4. Deploy ./public to master branch
    ↓
GitHub Pages serves master → darshit.dev
```

## Components

### 1. GitHub Actions Workflow (`.github/workflows/deploy.yml`)

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

**Key Settings:**
- `publish_branch: master` - deploys to master (not default gh-pages)
- `force_orphan: true` - clean master history each deploy (no accumulation)
- `GITHUB_TOKEN` - no SSH key setup required
- `hugo-version: '0.140.0'` - pinned version for stability
- `keep_files: true` - optional, doesn't affect behavior since CNAME comes from Hugo build

### 2. Branch Strategy

| Branch | Purpose | Who Pushes |
|--------|---------|------------|
| `hugo` | Hugo source files | Developer (manual) |
| `master` | Generated HTML | GitHub Actions (automatic) |

**Developer workflow:**
```bash
git add content/posts/new-post.md
git commit -m "new post"
git push origin hugo
# Site auto-deploys ~30 seconds later
```

### 3. Migration Steps

**Phase 1: Create hugo branch**
```bash
cd /Users/darshit/Projects/darshitpp.github.io
git checkout --orphan hugo
git rm -rf .  # master untouched
# Copy all blog/ content here (exclude public/, .gitmodules, .git/)
git add .
git commit -m "migrate hugo source"
git push origin hugo
```

**Phase 1a: CNAME Handling (CRITICAL)**
The CNAME file must be in Hugo's `static/` directory so it's included in the build output:
```bash
git show master:CNAME > static/CNAME
```
This ensures `darshit.dev` custom domain continues working after migration.

**Phase 2: Add Actions workflow**
- Create `.github/workflows/deploy.yml`
- Commit and push to `hugo`

**Phase 3: Verify deployment**
- Check Actions tab for workflow run
- Verify darshit.dev loads
- Verify CNAME preserved

**Phase 4: Preserve fallback**
- Old two-repo setup remains untouched
- Old deploy script works if needed

## Error Handling

### Migration Failures
- **Mid-copy failure:** `master` branch untouched, delete `hugo` branch, retry
- **Push failure:** Local state only, no remote impact

### Runtime Failures
- **Hugo build fails:** Actions job fails, `master` unchanged, site stays live
- **Deploy step fails:** `master` unchanged, retry via Actions re-run
- **Site breaks post-deploy:** `git revert HEAD` on `hugo` → triggers redeploy

### Rollback Procedures

| Scenario | Action |
|----------|--------|
| Migration breaks | Delete `hugo` branch, continue using old script |
| Actions workflow fails | Old deploy script still functional |
| Site content breaks | `git revert HEAD` on `hugo` branch |
| Immediate rollback needed | Revert last commit on `master` via GitHub UI |

## Testing Strategy

### Pre-Migration Safety Checks
1. Verify Hugo installed locally (`hugo version`)
2. Verify git connectivity to both remotes
3. Verify both repos are clean (no uncommitted changes)
4. Verify both repos are synced with remote
5. Create backup branch: `backup-pre-migration`
6. Verify current live site is accessible (HTTP 200)
7. Verify CNAME exists on master
8. Save backup SHA to persistent location (`~/hugo-migration-master-backup.txt`)

### Mid-Migration Checkpoints
1. **After creating hugo branch:** Verify master untouched, verify hugo branch on remote
2. **After copying files:** Verify CNAME in `static/CNAME`
3. **Before pushing to GitHub:** Run local Hugo build, verify build succeeds, verify CNAME in output
4. **After pushing:** Verify Actions triggered, verify master updated

### Post-Migration Verification
1. Push test change to `hugo` branch
2. Verify Actions completes successfully
3. Verify darshit.dev loads with test change
4. Verify CNAME preserved (no domain errors)
5. Revert test commit
6. Verify site reverts to previous state
7. Verify backup branch exists
8. Verify old deploy script still works (fallback check)

### Rollback Test
1. Revert test commit on `hugo`
2. Verify site reverts to previous state

## Trade-offs

### Option Considered: `/docs` Folder
- **Rejected** because: requires GitHub Pages to serve from `/docs` path, may affect custom domain configuration

### Option Considered: Simplified Local Deploy
- **Rejected** because: still requires manual deploy script, doesn't achieve "single push" goal

### Chosen: GitHub Actions
- **Pros:** Single push deploys, no branch switching, automated, consistent
- **Cons:** Requires Actions setup, less manual control

## Files to Migrate

From `blog/` to `darshitpp.github.io/hugo`:
- `content/` (all posts, pages)
- `config.yml`
- `themes/` (PaperMod)
- `static/`
- `layouts/`
- `archetypes/`
- `.gitignore` (updated for Hugo)

**Exclude:**
- `public/` (generated, not needed in source)
- `.gitmodules` (no submodules in new setup)
- `blog/.git/` (fresh repo)

## Success Criteria

1. ✅ Single repository (`darshitpp.github.io`)
2. ✅ `git push origin hugo` deploys site
3. ✅ No manual branch switching
4. ✅ `darshit.dev` resolves correctly
5. ✅ Rollback possible via `git revert`
6. ✅ Old deploy script preserved as fallback

## Appendix: Old Deploy Script (Preserved)

Location: `deploy-website.sh` (kept for fallback)

Purpose: Documents original two-repo workflow if Actions fails.
