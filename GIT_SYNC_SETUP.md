# Git Repository Sync Setup Guide

## Step 1: Initialize Local Git Repository

Open your terminal/command prompt in the project directory and run:

```bash
# Initialize git repository
git init

# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial commit - VibeQA Generator v1.0"
```

## Step 2: Link to Remote Repository

```bash
# Add the remote repository
git remote add origin https://github.com/ukm2020/VibeQA.git

# Verify the remote was added correctly
git remote -v
```

## Step 3: Sync with Remote Repository

Since you manually uploaded files, we need to handle potential conflicts:

```bash
# Fetch the remote content
git fetch origin

# Pull and merge with allow unrelated histories (since both have content)
git pull origin main --allow-unrelated-histories

# If there are merge conflicts, resolve them, then:
git add .
git commit -m "Merge remote repository with local project"

# Push your complete project to GitHub
git push -u origin main
```

## Step 4: Verify Synchronization

```bash
# Check status
git status

# View commit history
git log --oneline

# Verify remote connection
git remote show origin
```

## Step 5: Future Workflow Commands

### Daily Development Workflow:
```bash
# Before starting work - pull latest changes
git pull origin main

# After making changes - stage, commit, and push
git add .
git commit -m "Your descriptive commit message"
git push origin main
```

### Useful Git Commands:
```bash
# Check what files have changed
git status

# See differences in files
git diff

# View commit history
git log --oneline

# Create and switch to new branch
git checkout -b feature-branch-name

# Switch back to main branch
git checkout main
```

## Troubleshooting Common Issues

### If you get "fatal: refusing to merge unrelated histories":
```bash
git pull origin main --allow-unrelated-histories --no-edit
```

### If you get authentication errors:
```bash
# Use personal access token instead of password
# When prompted for password, use your GitHub Personal Access Token
```

### If files are out of sync:
```bash
# Force push (use carefully!)
git push origin main --force

# Or reset to match remote exactly
git reset --hard origin/main
```

## Setting Up Git Credentials (Optional)

To avoid entering credentials repeatedly:

```bash
# Cache credentials for 1 hour
git config --global credential.helper 'cache --timeout=3600'

# Or store credentials permanently (less secure)
git config --global credential.helper store
```

## Verification Checklist

After setup, verify:
- [ ] `git status` shows "On branch main" and "nothing to commit, working tree clean"
- [ ] `git remote -v` shows your GitHub repository URL
- [ ] GitHub repository shows all your local files
- [ ] You can successfully push and pull changes

## Next Steps

1. **Run the commands above in sequence**
2. **Test by making a small change and pushing it**
3. **Verify the change appears on GitHub**
4. **Set up branch protection rules on GitHub (optional)**

Your local project will now be fully synchronized with the GitHub repository!
