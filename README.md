# Darshit Patel's Blog (Hugo Source)

This repository contains the Hugo source files for my blog [darshit.dev](https://darshit.dev).

## Workflow (Consolidated)

From now on, use this repository for all blog updates:

1.  **Work on `hugo` branch:** Always make your changes (new posts, theme updates, config changes) on the `hugo` branch.
2.  **Deploy via Push:** To deploy your changes, simply commit and push to the `hugo` branch:
    ```bash
    git add .
    git commit -m "New post: Title"
    git push origin hugo
    ```
3.  **Automatic Deployment:** GitHub Actions will automatically:
    - Build the site using Hugo (version: latest).
    - Deploy the generated HTML to the `master` branch (which GitHub Pages serves).

## Rollback

If a deployment fails or breaks the site:
1.  Revert the commit on the `hugo` branch.
2.  Push to `hugo`.
3.  The `master` branch will be automatically updated with the previous version.

## Fallback (Old Workflow)

The old `blog/` repository and `deploy-website.sh` are still available as a fallback but are no longer the primary workflow.
